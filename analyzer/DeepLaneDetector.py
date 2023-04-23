import torch
import torchvision.transforms as transforms
from torch.onnx import export
from PIL import Image
import onnx
import onnxruntime
import numpy as np
import scipy
import cv2
from constant.constant import culane_row_anchor
from analyzer import device


class DeepLaneDetector:

    def __init__(self):
        self.detector = onnxruntime.InferenceSession('model/lane/utral-fast/culane_18.onnx')

        self.row_anchor = culane_row_anchor
        self.cls_num_per_lane = 18
        self.col_sample = np.linspace(0, 800 - 1, 200)
        self.col_sample_w = self.col_sample[1] - self.col_sample[0]

        self.img_transforms = transforms.Compose([
          transforms.Resize((288, 800)),
          transforms.ToTensor(),
          transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
    ])
    def detect(self, frame):
        vis = frame.copy()
        img_w, img_h = frame.shape[1], frame.shape[0]
        # frame = np.transpose(frame, (2, 0, 1))
        # 转为int8
        # frame = frame.astype(np.uint8)
        # print('frame = ',frame)
        frame = Image.fromarray(frame)
        frame = self.img_transforms(frame).unsqueeze(0)
        ort_inputs = {self.detector.get_inputs()[0].name: self.to_numpy(frame)}
        ort_outs = self.detector.run(None, ort_inputs)

        ort_outs = ort_outs[0][0]

        ort_outs = ort_outs[:, ::-1, :]
        prob = scipy.special.softmax(ort_outs[:-1, :, :], axis=0)
        idx = np.arange(200) + 1
        idx = idx.reshape(-1, 1, 1)
        loc = np.sum(prob * idx, axis=0)
        out_j = np.argmax(ort_outs, axis=0)
        loc[out_j == 200] = 0
        out_j = loc

        for i in range(out_j.shape[1]):
          if np.sum(out_j[:, i] != 0) > 2:
              for k in range(out_j.shape[0]):
                  if out_j[k, i] > 0:
                      ppp = (int(out_j[k, i] * self.col_sample_w * img_w / 800) - 1, int(img_h * (self.row_anchor[self.cls_num_per_lane-1-k]/288)) - 1 )
                      cv2.circle(vis,ppp,5,(0,255,0),-1)

        return vis  
    
    def to_numpy(self, tensor):
      return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()