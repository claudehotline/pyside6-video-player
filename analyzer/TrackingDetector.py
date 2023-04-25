import numpy as np
from analyzer.BaseDetector import baseDet
from analyzer.YoloDetector import YoloDetector

class TrackingDetector(baseDet):

    def __init__(self):
        super(TrackingDetector, self).__init__()
        self.model = YoloDetector('model/detect/rtmdet-m')
        
    def getbox(self, im):
        bboxes, labels = self.model.getbox(im)
        num_box = len(bboxes)

        pred_boxes = np.zeros((num_box, 6))
        pred_boxes[:, 0:4] = bboxes[:, :4]
        pred_boxes[:, 4] = labels
        pred_boxes[:, 5] = bboxes[:, 4]

        return im, pred_boxes