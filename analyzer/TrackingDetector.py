import numpy as np
from analyzer.YoloDetector import YoloDetector
from utils.bytetrack.byte_tracker import BYTETracker
from utils.cal_speed import Speed
import cv2

class TrackingDetector:

    def __init__(self, model_path1, model_path2, tracking_class=[]):
        self.model = YoloDetector(model_path1, tracking_class)
        self.tracker = BYTETracker(det_thresh=0.6, 
                    track_thresh=0.2, track_buffer=70, 
                    match_thresh=0.9, frame_rate=30)
        self.frameCounter = 0
        self.prev_bboxes = []
    
    def detect(self, frame):
        bboxes2draw = self.update_tracker(frame)
        if self.frameCounter % 10 == 0:
            self.prev_bboxes = bboxes2draw
        image = self.drawbox(frame, bboxes2draw)
        self.frameCounter += 1
        return image
    
    def update_tracker(self, image):
        bboxes, _ = self.model.getbox(image)
        bboxes2draw = self.tracker.update(bboxes, (image.shape[1], image.shape[0]), (image.shape[1], image.shape[0]))
        bboxes2draw = np.array([[int(box.tlbr[0]), int(box.tlbr[1]), int(box.tlbr[2]), int(box.tlbr[3]), 2, int(box.track_id)]  for box in bboxes2draw])
        return bboxes2draw
    
    def drawbox(self, image, bboxes, line_thickness=None):
        tl = line_thickness or round(
            0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
        for (x1, y1, x2, y2, cls_id, track_id) in bboxes:
            c1, c2 = (x1, y1), (x2, y2)
            color = (0, 255, 0)
            cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(str(cls_id), 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3

            cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
            
            location_two = x1, y1, x2-x1, y2-y1
            # 获取 self.prev_bboxes[5] = track_id 的 bbox
            location_one = self.prev_bboxes[self.prev_bboxes[...,5] == track_id]
            # print('location_one length = ', len(location_one))
            if len(location_one) > 0:
                location_one = location_one[0]
                location_one = location_one[0], location_one[1], location_one[2] - location_one[0], location_one[3] - location_one[1]
                speed = Speed(location_one, location_two)
                cv2.putText(image, '{} ID-{} speed-{:.2f} km/h'.format(str(cls_id), track_id, speed), (c1[0], c1[1] - 2), 0, tl / 3,
                        [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
            else:
                cv2.putText(image, '{} ID-{}'.format(str(cls_id), track_id), (c1[0], c1[1] - 2), 0, tl / 3,
                        [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
            # cv2.putText(image, '{} ID-{}'.format(str(cls_id), track_id), (c1[0], c1[1] - 2), 0, tl / 3,
            #              [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
            
            
        return image