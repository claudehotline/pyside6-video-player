import argparse
import torch
import _init_paths
from lib.models.stark.repvgg import repvgg_model_convert
from lib.models.stark import build_starks
from lib.config.stark_s.config import cfg, update_config_from_file
import torch.nn as nn
import torch.nn.functional as F
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


def get_data(bs, sz):
    img_patch = torch.randn(bs, 3, sz, sz, requires_grad=True)
    mask = torch.rand(bs, sz, sz, requires_grad=True) > 0.5
    return img_patch, mask


class Backbone_Bottleneck_PE(nn.Module):
    def __init__(self, backbone, bottleneck, position_embed):
        super(Backbone_Bottleneck_PE, self).__init__()
        self.backbone = backbone
        self.bottleneck = bottleneck
        self.position_embed = position_embed

    def forward(self, img: torch.Tensor, mask: torch.Tensor):
        # feat = self.bottleneck(self.backbone(img))  # BxCxHxW
        output_back, pos = self.backbone(img, mask)
        src_feat, mask = output_back[-1].decompose()
        feat = self.bottleneck(src_feat)

        # adjust shape
        feat_vec = feat.flatten(2).permute(2, 0, 1)  # HWxBxC
        pos_embed_vec = pos[-1].flatten(2).permute(2, 0, 1)  # HWxBxC
        mask_vec = mask.flatten(1)  # BxHW
        return feat_vec, mask_vec, pos_embed_vec


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


if __name__ == "__main__":
    load_checkpoint = True
    save_name = "stark_s_backbone_bottleneck_pe.onnx"
    """update cfg"""
    args = parse_args()
    yaml_fname = 'experiments/%s/%s.yaml' % (args.script, args.config)
    update_config_from_file(yaml_fname)
    '''set some values'''
    bs = 1
    z_sz = 128
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
    # print('backbone: ', backbone)
    bottleneck = model.bottleneck
    position_embed = model.query_embed
    torch_model = Backbone_Bottleneck_PE(backbone, bottleneck, position_embed)
    # print(torch_model)
    # get the template
    img_z, mask_z = get_data(bs, z_sz)
    # forward the template
    # tensorlist = NestedTensor(img_z, mask_z)
    # print("tensorlist: ", tensorlist)
    # torch_outs = torch_model(tensorlist)
    # torch_outs = torch_model(nested_tensor)
    torch_outs = torch_model(img_z, mask_z)
    torch.onnx.export(torch_model,  # model being run
                      (img_z, mask_z),  # model input (or a tuple for multiple inputs)
                      save_name,  # where to save the model (can be a file or file-like object)
                      export_params=True,  # store the trained parameter weights inside the model file
                      opset_version=11,  # the ONNX version to export the model to
                      do_constant_folding=True,  # whether to execute constant folding for optimization
                      input_names=['img_z', 'mask_z'],  # the model's input names
                      output_names=['feat', 'mask', 'pos'],  # the model's output names
                      # dynamic_axes={'input': {0: 'batch_size'},  # variable length axes
                      #               'output': {0: 'batch_size'}}
                      )
    # latency comparison
    N = 1000
    """########## inference with the pytorch model ##########"""
    # torch_model = torch_model.cuda()
    s = time.time()
    for i in range(N):
        # img_z_cuda, mask_z_cuda = img_z.cuda(), mask_z.cuda()
        # _ = torch_model(img_z_cuda, mask_z_cuda)
        _ = torch_model(img_z, mask_z)
    e = time.time()
    print("pytorch model average latency: %.2f ms" % ((e - s) / N * 1000))
    """########## inference with the onnx model ##########"""
    onnx_model = onnx.load(save_name)
    onnx.checker.check_model(onnx_model)

    ort_session = onnxruntime.InferenceSession(save_name)

    # compute ONNX Runtime output prediction
    ort_inputs = {'img_z': to_numpy(img_z),
                  'mask_z': to_numpy(mask_z)}
    # print(onnxruntime.get_device())
    # warmup
    for i in range(10):
        ort_outs = ort_session.run(None, ort_inputs)
    s = time.time()
    for i in range(N):
        ort_outs = ort_session.run(None, ort_inputs)
    e = time.time()
    print("onnx model average latency: %.2f ms" % ((e - s) / N * 1000))
    # compare ONNX Runtime and PyTorch results
    for i in range(3):
        np.testing.assert_allclose(to_numpy(torch_outs[i]), ort_outs[i], rtol=1e-03, atol=1e-05)

    print("Exported model has been tested with ONNXRuntime, and the result looks good!")
