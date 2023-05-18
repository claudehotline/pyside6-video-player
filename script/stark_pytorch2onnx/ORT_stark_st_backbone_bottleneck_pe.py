import argparse
import torch
import _init_paths
from lib.models.stark.repvgg import repvgg_model_convert
from lib.models.stark import build_starkst
from lib.config.stark_st1.config import cfg, update_config_from_file
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
    parser.add_argument('--script', type=str, default='stark_st1', help='script name')
    parser.add_argument('--config', type=str, default='baseline', help='yaml configure file name')
    args = parser.parse_args()
    return args


def get_data(bs, sz):
    img_patch = torch.randn(bs, 3, sz, sz, requires_grad=True)
    mask = torch.rand(bs, sz, sz, requires_grad=True) > 0.5
    return img_patch, mask


class Backbone_Bottleneck_PE(nn.Module):
    def __init__(self, backbone, bottleneck):
        super(Backbone_Bottleneck_PE, self).__init__()
        self.backbone = backbone
        self.bottleneck = bottleneck

    def forward(self, img: torch.Tensor, mask: torch.Tensor):
        # feat = self.bottleneck(self.backbone(img))  # BxCxHxW
        return self.forward_backbone(img, mask)
    
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
        return feat_vec, mask_vec, pos_embed_vec


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()


if __name__ == "__main__":
    load_checkpoint = True
    save_name = "stark_st1_backbone_bottleneck_pe.onnx"
    """update cfg"""
    args = parse_args()
    yaml_fname = 'experiments/%s/%s.yaml' % (args.script, args.config)
    update_config_from_file(yaml_fname)
    '''set some values'''
    bs = 1
    z_sz = 128
    # build the stark model
    model = build_starkst(cfg)
    # load checkpoint
    if load_checkpoint:
        checkpoint_name = 'checkpoints\STARKST_ep0050.pth.tar'
        model.load_state_dict(torch.load(checkpoint_name, map_location='cpu')['net'], strict=True)
    # transfer to test mode
    model = repvgg_model_convert(model)
    model.eval()
    # print(model)
    """ rebuild the inference-time model """
    backbone = model.backbone
    bottleneck = model.bottleneck
    torch_model = Backbone_Bottleneck_PE(backbone, bottleneck)
    # print(torch_model)
    # get the template
    img_z, mask_z = get_data(bs, z_sz)
    # forward the template
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
