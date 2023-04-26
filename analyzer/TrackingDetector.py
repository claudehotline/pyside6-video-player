import numpy as np
from analyzer.YoloDetector import YoloDetector
from utils.tracker import update_tracker
import cv2

class TrackingDetector:

    def __init__(self, model_path, tracking_class=[]):
        # super(TrackingDetecor, self).__init__()
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
    
    def detect(self, frame):

        self.frameCounter += 1
        bboxes2draw = update_tracker(self, frame)
        self.drawbox(frame, bboxes2draw)
        return frame
    
    def drawbox(self, image, bboxes, line_thickness=None):
        # count_line_height = 110

        # Plots one bounding box on image img
        tl = line_thickness or round(
            0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
        for (x1, y1, x2, y2, cls_id, track_id) in bboxes:
            c1, c2 = (x1, y1), (x2, y2)
            color = (0, 255, 0)
            cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(cls_id, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(image, '{} ID-{}'.format(cls_id, track_id), (c1[0], c1[1] - 2), 0, tl / 3,
                        [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
            
            # 检测框的中心点坐标
            # cx = int((x1+x2)/2)
            # cy = int((y1+y2)/2)

            # img_w = image.shape[1]
            # cv2.line(image, (0, 120), (img_w, 120), (255, 0, 0), 2)
            # # cv2.line(image, (360, 0), (360, img_h), (255, 0, 0), 2)

            # cv2.putText(image, 'up: {}'.format(len(self.car_count_up)), (10, 200), 0, 5, [225, 255, 255], thickness=2, lineType=cv2.LINE_AA)
            # cv2.putText(image, 'dwon: {}'.format(len(self.car_count_down)), (10, 300), 0, 5, [225, 255, 255], thickness=2, lineType=cv2.LINE_AA)

            # # 在image上画出cx,cy
            # cv2.circle(image, (cx, cy), 2, (0, 0, 255), 2, cv2.FILLED)

            # # 统计上行车辆的数量
            # if cx > 360 and cy >count_line_height - 20 and cy < count_line_height + 20:
            #     if track_id not in self.car_count_up:
            #         self.car_count_up.append(track_id)

            # # 统计下行车辆的数量
            # if cx <= 360 and cy >count_line_height - 20 and cy < count_line_height + 20:
            #     if track_id not in self.car_count_down:
            #         self.car_count_down.append(track_id)