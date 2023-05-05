from PySide6.QtCore import Signal
from PySide6.QtCore import QObject
from analyzer.TrackingDetector import TrackingDetector
import cv2

class CarCountDetector(TrackingDetector, QObject):
    car_count = Signal(int, int)

    def __init__(self, model_path1, model_path2, tracking_class=[]):
        QObject.__init__(self)
        TrackingDetector.__init__(self, model_path1, model_path2, tracking_class)
        self.car_count_up = []
        self.car_count_down = []
    
    def drawbox(self, image, bboxes, line_thickness=None):
        count_line_height = 110

        # Plots one bounding box on image img
        tl = line_thickness or round(0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
        for (x1, y1, x2, y2, cls_id, track_id) in bboxes:
            c1, c2 = (x1, y1), (x2, y2)
            color = (0, 255, 0)
            
            # 在image上画出检测框
            cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
            tf = max(tl - 1, 1)  # font thickness
            # 在image上画出track_id
            cv2.putText(image, 'ID-{}'.format(track_id), (c1[0], c1[1] - 2), 0, tl / 3,
                        [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)
            
            # 检测框的中心点坐标
            cx = int((x1+x2)/2)
            cy = int((y1+y2)/2)

            # 在image上画出虚拟线圈
            img_w = image.shape[1]
            cv2.line(image, (0, 120), (img_w, 120), (255, 0, 0), 2)
            # cv2.line(image, (360, 0), (360, img_h), (255, 0, 0), 2)

            # 在image上画出cx,cy
            cv2.circle(image, (cx, cy), 2, (0, 0, 255), 2, cv2.FILLED)

            # 统计上行车辆的数量
            if cx > 360 and cy >count_line_height - 20 and cy < count_line_height + 20:
                if track_id not in self.car_count_up:
                    self.car_count_up.append(track_id)

            # 统计下行车辆的数量
            if cx <= 360 and cy >count_line_height - 20 and cy < count_line_height + 20:
                if track_id not in self.car_count_down:
                    self.car_count_down.append(track_id)

            self.car_count.emit(len(self.car_count_up), len(self.car_count_down))
            # 在image上画出统计信息
            # cv2.putText(image, 'up: {}'.format(len(self.car_count_up)), (10, 200), 0, 5, [225, 255, 255], thickness=2, lineType=cv2.LINE_AA)
            # cv2.putText(image, 'dwon: {}'.format(len(self.car_count_down)), (10, 300), 0, 5, [225, 255, 255], thickness=2, lineType=cv2.LINE_AA)