import argparse
import torch
import _init_paths
from lib.models.stark.repvgg import repvgg_model_convert
from lib.models.stark import build_starks
from lib.config.stark_s.config import cfg, update_config_from_file
from lib.utils.box_ops import box_xyxy_to_cxcywh
import torch.nn as nn
import torch.nn.functional as F
# for onnx conversion and inference
import torch.onnx
import numpy as np
import onnx
import onnxruntime
import time
import os
from lib.test.evaluation.environment import env_settings


def parse_args():
    parser = argparse.ArgumentParser(description='Parse args for training')
    parser.add_argument('--script', type=str, default='stark_s', help='script name')
    parser.add_argument('--config', type=str, default='baseline', help='yaml configure file name')
    args = parser.parse_args()
    return args


def get_data(bs=1, sz_x=320, hw_z=64, c=256):
    img_x = torch.randn(bs, 3, sz_x, sz_x, requires_grad=True)
    mask_x = torch.rand(bs, sz_x, sz_x, requires_grad=True) > 0.5
    feat_vec_z = torch.randn(hw_z, bs, c, requires_grad=True)  # HWxBxC
    mask_vec_z = torch.rand(bs, hw_z, requires_grad=True) > 0.5  # BxHW
    pos_vec_z = torch.randn(hw_z, bs, c, requires_grad=True)  # HWxBxC
    return img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z


class STARK(nn.Module):
    def __init__(self, backbone, bottleneck, position_embed, transformer, box_head):
        super(STARK, self).__init__()
        self.backbone = backbone
        self.bottleneck = bottleneck
        self.query_embed = position_embed
        self.transformer = transformer
        self.head_type = 'CORNER'
        self.box_head = box_head
        self.feat_sz_s = int(box_head.feat_sz)
        self.feat_len_s = int(box_head.feat_sz ** 2)

    def forward(self, img: torch.Tensor, mask: torch.Tensor,
                feat_vec_z: torch.Tensor, mask_vec_z: torch.Tensor, pos_vec_z: torch.Tensor):
        
        x_dict = self.forward_backbone(img, mask)
        z_dict1 = {"feat": feat_vec_z, "mask": mask_vec_z, "pos": pos_vec_z}

        feat_dict_list = [z_dict1, x_dict]

        seq_dict = merge_template_search(feat_dict_list)

        out_dict, _, _ = self.forward_transformer(seq_dict=seq_dict, run_box_head=True)

        pred_boxes = out_dict['pred_boxes'].view(-1, 4)
        pred_box = pred_boxes.mean(dim=0)

        return pred_box
    
    def forward_backbone(self, img: torch.Tensor, mask: torch.Tensor):
        """The input type is NestedTensor, which consists of:
               - tensor: batched images, of shape [batch_size x 3 x H x W]
               - mask: a binary mask of shape [batch_size x H x W], containing 1 on padded pixels
        """
        # assert isinstance(input, NestedTensor)
        # Forward the backbone
        output_back, pos = self.backbone(img, mask)  # features & masks, position embedding for the search
        # Adjust the shapes
        return self.adjust(output_back, pos)
    
    def adjust(self, output_back: list, pos_embed: list):
        """
        """
        src_feat, mask = output_back[-1].decompose()
        assert mask is not None
        # reduce channel
        feat = self.bottleneck(src_feat)  # (B, C, H, W)
        # adjust shapes
        feat_vec = feat.flatten(2).permute(2, 0, 1)  # HWxBxC
        pos_embed_vec = pos_embed[-1].flatten(2).permute(2, 0, 1)  # HWxBxC
        mask_vec = mask.flatten(1)  # BxHW
        return {"feat": feat_vec, "mask": mask_vec, "pos": pos_embed_vec}
    
    def forward_transformer(self, seq_dict, run_box_head=True, run_cls_head=False):
        # if self.aux_loss:
        #     raise ValueError("Deep supervision is not supported.")
        # Forward the transformer encoder and decoder
        output_embed, enc_mem = self.transformer(seq_dict["feat"], seq_dict["mask"], self.query_embed.weight,
                                                 seq_dict["pos"], return_encoder_output=True)
        # Forward the corner head
        out, outputs_coord = self.forward_box_head(output_embed, enc_mem)
        return out, outputs_coord, output_embed
    
    def forward_box_head(self, hs, memory):
        """
        hs: output embeddings (1, B, N, C)
        memory: encoder embeddings (HW1+HW2, B, C)"""
        if self.head_type == "CORNER":
            # adjust shape
            enc_opt = memory[-self.feat_len_s:].transpose(0, 1)  # encoder output for the search region (B, HW, C)
            dec_opt = hs.squeeze(0).transpose(1, 2)  # (B, C, N)
            att = torch.matmul(enc_opt, dec_opt)  # (B, HW, N)
            opt = (enc_opt.unsqueeze(-1) * att.unsqueeze(-2)).permute((0, 3, 2, 1)).contiguous()  # (B, HW, C, N) --> (B, N, C, HW)
            bs, Nq, C, HW = opt.size()
            opt_feat = opt.view(-1, C, self.feat_sz_s, self.feat_sz_s)
            # run the corner head
            outputs_coord = box_xyxy_to_cxcywh(self.box_head(opt_feat))
            outputs_coord_new = outputs_coord.view(bs, Nq, 4)
            out = {'pred_boxes': outputs_coord_new}
            return out, outputs_coord_new
        elif self.head_type == "MLP":
            # Forward the class and box head
            outputs_coord = self.box_head(hs).sigmoid()
            out = {'pred_boxes': outputs_coord[-1]}
            if self.aux_loss:
                out['aux_outputs'] = self._set_aux_loss(outputs_coord)
            return out, outputs_coord

def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

def merge_template_search(inp_list, return_search=False, return_template=False):
    """NOTICE: search region related features must be in the last place"""
    seq_dict = {"feat": torch.cat([x["feat"] for x in inp_list], dim=0),
                "mask": torch.cat([x["mask"] for x in inp_list], dim=1),
                "pos": torch.cat([x["pos"] for x in inp_list], dim=0)}
    if return_search:
        x = inp_list[-1]
        seq_dict.update({"feat_x": x["feat"], "mask_x": x["mask"], "pos_x": x["pos"]})
    if return_template:
        z = inp_list[0]
        seq_dict.update({"feat_z": z["feat"], "mask_z": z["mask"], "pos_z": z["pos"]})
    return seq_dict

if __name__ == "__main__":
    load_checkpoint = True
    save_name = "stark_s_complete.onnx"
    # update cfg
    args = parse_args()
    yaml_fname = 'experiments/%s/%s.yaml' % (args.script, args.config)
    update_config_from_file(yaml_fname)
    # build the stark model
    model = build_starks(cfg)
    # load checkpoint
    if load_checkpoint:
        # save_dir = env_settings().save_dir
        # checkpoint_name = os.path.join(save_dir,
        #                                "checkpoints/train/%s/%s/STARKLightningXtrt_ep0500.pth.tar"
        #                                % (args.script, args.config))
        checkpoint_name = 'checkpoints\STARKS_ep0500.pth.tar'
        model.load_state_dict(torch.load(checkpoint_name, map_location='cpu')['net'], strict=True)
    # transfer to test mode
    model = repvgg_model_convert(model)
    model.eval()
    """ rebuild the inference-time model """
    backbone = model.backbone
    bottleneck = model.bottleneck
    position_embed = model.query_embed
    transformer = model.transformer
    box_head = model.box_head
    box_head.coord_x = box_head.coord_x.cpu()
    box_head.coord_y = box_head.coord_y.cpu()
    torch_model = STARK(backbone, bottleneck, position_embed, transformer, box_head)
    print(torch_model)
    torch.save(torch_model.state_dict(), "complete.pth")
    # get the network input
    # bs = 1
    # sz_x = cfg.TEST.SEARCH_SIZE
    # FEAT_SIZE = 8
    # hw_z = cfg.DATA.TEMPLATE.FEAT_SIZE ** 2
    # hw_z = 8 ** 2
    # c = cfg.MODEL.HIDDEN_DIM
    # print(bs, sz_x, hw_z, c)
    # img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z = get_data(bs=bs, sz_x=sz_x, hw_z=hw_z, c=c)
    img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z = get_data()
    torch_outs = torch_model(img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z)
    torch.onnx.export(torch_model,  # model being run
                      (img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z),  # model input (a tuple for multiple inputs)
                      save_name,  # where to save the model (can be a file or file-like object)
                      export_params=True,  # store the trained parameter weights inside the model file
                      opset_version=11,  # the ONNX version to export the model to
                      do_constant_folding=True,  # whether to execute constant folding for optimization
                      input_names=['img_x', 'mask_x', 'feat_vec_z', 'mask_vec_z', 'pos_vec_z'],  # model's input names
                      output_names=['outputs_coord'],  # the model's output names
                      # dynamic_axes={'input': {0: 'batch_size'},  # variable length axes
                      #               'output': {0: 'batch_size'}}
                      )
    """########## inference with the pytorch model ##########"""
    # forward the template
    # N = 1000
    N = 50
    # torch_model = torch_model.cuda()
    # torch_model.box_head.coord_x = torch_model.box_head.coord_x.cuda()
    # torch_model.box_head.coord_y = torch_model.box_head.coord_y.cuda()

    torch_model = torch_model
    torch_model.box_head.coord_x = torch_model.box_head.coord_x
    torch_model.box_head.coord_y = torch_model.box_head.coord_y

    """########## inference with the onnx model ##########"""
    onnx_model = onnx.load(save_name)
    onnx.checker.check_model(onnx_model)
    print("creating session...")
    ort_session = onnxruntime.InferenceSession(save_name)
    # ort_session.set_providers(["TensorrtExecutionProvider"],
    #                   [{'device_id': '1', 'trt_max_workspace_size': '2147483648', 'trt_fp16_enable': 'True'}])
    print("execuation providers:")
    print(ort_session.get_providers())
    # compute ONNX Runtime output prediction
    """warmup (the first one running latency is quite large for the onnx model)"""
    for i in range(50):
        print(i)
        # pytorch inference
        # img_x_cuda, mask_x_cuda, feat_vec_z_cuda, mask_vec_z_cuda, pos_vec_z_cuda = \
        #     img_x.cuda(), mask_x.cuda(), feat_vec_z.cuda(), mask_vec_z.cuda(), pos_vec_z.cuda()
        # torch_outs = torch_model(img_x_cuda, mask_x_cuda, feat_vec_z_cuda, mask_vec_z_cuda, pos_vec_z_cuda)
        torch_outs = torch_model(img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z)
        # onnx inference
        ort_inputs = {'img_x': to_numpy(img_x),
                      'mask_x': to_numpy(mask_x),
                      'feat_vec_z': to_numpy(feat_vec_z),
                      'mask_vec_z': to_numpy(mask_vec_z),
                      'pos_vec_z': to_numpy(pos_vec_z)
                      }
        s_ort = time.time()
        ort_outs = ort_session.run(None, ort_inputs)
    """begin the timing"""
    t_pyt = 0  # pytorch time
    t_ort = 0  # onnxruntime time

    for i in range(N):
        print(i)
        # generate data
        img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z = get_data()
        # pytorch inference
        # img_x_cuda, mask_x_cuda, feat_vec_z_cuda, mask_vec_z_cuda, pos_vec_z_cuda = \
        #     img_x.cuda(), mask_x.cuda(), feat_vec_z.cuda(), mask_vec_z.cuda(), pos_vec_z.cuda()
        s_pyt = time.time()
        # torch_outs = torch_model(img_x_cuda, mask_x_cuda, feat_vec_z_cuda, mask_vec_z_cuda, pos_vec_z_cuda)
        torch_outs = torch_model(img_x, mask_x, feat_vec_z, mask_vec_z, pos_vec_z)
        e_pyt = time.time()
        lat_pyt = e_pyt - s_pyt
        t_pyt += lat_pyt
        # print("pytorch latency: %.2fms" % (lat_pyt * 1000))
        # onnx inference
        ort_inputs = {'img_x': to_numpy(img_x),
                      'mask_x': to_numpy(mask_x),
                      'feat_vec_z': to_numpy(feat_vec_z),
                      'mask_vec_z': to_numpy(mask_vec_z),
                      'pos_vec_z': to_numpy(pos_vec_z)
                      }
        s_ort = time.time()
        ort_outs = ort_session.run(None, ort_inputs)
        e_ort = time.time()
        lat_ort = e_ort - s_ort
        t_ort += lat_ort
        # print("onnxruntime latency: %.2fms" % (lat_ort * 1000))
    print("pytorch model average latency", t_pyt/N*1000)
    print("onnx model average latency:", t_ort/N*1000)

    # # compare ONNX Runtime and PyTorch results
    # np.testing.assert_allclose(to_numpy(torch_outs), ort_outs[0], rtol=1e-03, atol=1e-05)
    #
    # print("Exported model has been tested with ONNXRuntime, and the result looks good!")
