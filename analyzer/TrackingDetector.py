import numpy as np
# from analyzer.BaseDetector import baseDet
from analyzer.YoloDetector import YoloDetector
from utils.tracker import update_tracker

class TrackingDetector:

    def __init__(self, model_path, tracking_class=[]):
        super(TrackingDetector, self).__init__()
        self.model = YoloDetector(model_path, tracking_class)

        self.frameCounter = 0
        
    def getbox(self, im):
        bboxes, labels = self.model.getbox(im)
        num_box = len(bboxes)

        pred_boxes = np.zeros((num_box, 6))
        pred_boxes[:, 0:4] = bboxes[:, :4]
        pred_boxes[:, 4] = labels
        pred_boxes[:, 5] = bboxes[:, 4]

        return im, pred_boxes
    
    def detect(self, im):

        retDict = {
            'frame': None,
            'faces': None,
            'list_of_ids': None,
            'face_bboxes': []
        }
        self.frameCounter += 1

        im, faces, face_bboxes = update_tracker(self, im)

        retDict['frame'] = im
        retDict['faces'] = faces
        retDict['face_bboxes'] = face_bboxes

        return retDict['frame']