import torch
import numpy as np
from utils.experimental import attempt_load
from utils.general import non_max_suppression, scale_coords, letterbox
from utils.torch_utils import select_device
from utils.BaseDetector import baseDet
from analyzer.YoloDetector import YoloDetector


class TrackingDetector(baseDet):

    def __init__(self):
        super(TrackingDetector, self).__init__()
        self.init_model()
        self.build_config()

    def init_model(self):

        # self.weights = 'model/yolov5m.pt'
        # self.device = '0' if torch.cuda.is_available() else 'cpu'
        model = YoloDetector('model/detect/rtmdet-m')
        self.m = model

    def preprocess(self, img):

        img0 = img.copy()
        img = letterbox(img, new_shape=self.img_size)[0]
        img = img[:, :, ::-1].transpose(2, 0, 1)
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        # print('img: ', img)
        # 转成fp32
        img = img.float()  # 单精度
        # img = img.half()  # 半精度
        img /= 255.0  # 图像归一化
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        return img0, img

    def getbox(self, im):
        bboxes, labels = self.m.detect(im)
        num_box = len(bboxes)
        # 创建一个num_box行，6列的矩阵
        # 1至4列为坐标，5列为类别，6列为置信度
        pred_boxes = np.zeros((num_box, 6))
        pred_boxes[:, 0:4] = bboxes[:, :4]
        pred_boxes[:, 4] = labels
        pred_boxes[:, 5] = bboxes[:, 4]
            
        # print('pred_boxes: ', pred_boxes)

        return im, pred_boxes