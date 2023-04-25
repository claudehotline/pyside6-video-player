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

        self.weights = 'model/yolov5m.pt'
        self.device = '0' if torch.cuda.is_available() else 'cpu'
        # self.device = select_device(self.device)
        model = YoloDetector('model/detect/rtmdet-m')
        # model = attempt_load(self.weights, map_location=self.device)
        # model.to(self.device).eval()
        # model.half()
        # print(model)
        # torch.save(model, 'test.pt')
        self.m = model
        # self.names = model.module.names if hasattr(
        #     model, 'module') else model.names

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

    def detect(self, im):

        # im0, img = self.preprocess(im)

        # pred = self.m(im, augment=False)[0]
        bboxes, labels = self.m.detect(im)
        num_box = len(bboxes)
        # 创建一个num_box行，6列的矩阵
        # 1至4列为坐标，5列为类别，6列为置信度
        pred_boxes = np.zeros((num_box, 6))
        pred_boxes[:, 0:4] = bboxes[:, :4]
        pred_boxes[:, 4] = labels
        pred_boxes[:, 5] = bboxes[:, 4]
        # print('im: ', im)
        # print('bboxes: ', bboxes)
        # print('labels: ', labels)

        # scores = bboxes[:, 4]
        # print('scores: ', scores)
        # bboxes = bboxes[:, :4]
        # pred_boxes = zip(bboxes, labels, scores)
        # print('pred_boxes: ', )
        
        # pred = pred.float()
        # pred = non_max_suppression(pred, self.threshold, 0.4)

        # pred_boxes = []
        # for det in pred:

        #     if det is not None and len(det):
        #         det[:, :4] = scale_coords(
        #             img.shape[2:], det[:, :4], im0.shape).round()

        #         for *x, conf, cls_id in det:
        #             lbl = self.names[int(cls_id)]
        #             if not lbl in ['person', 'car', 'truck']:
        #                 continue
        #             x1, y1 = int(x[0]), int(x[1])
        #             x2, y2 = int(x[2]), int(x[3])
        #             pred_boxes.append(
        #                 (x1, y1, x2, y2, lbl, conf))
            
        print('pred_boxes: ', pred_boxes)

        return im, pred_boxes

