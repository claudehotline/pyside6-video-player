from PySide6.QtCore import QObject, Signal
import numpy as np
import time
import cv2
import os

from analyzer.YoloDetector import YoloDetector
from analyzer.Segmentor import Segment
from analyzer.PoseDetector import PoseDetect

class VideoFrameProcessor(QObject):
    
    result = Signal(np.ndarray)

    def __init__(self, detectType, model_list):
        super().__init__()

        self.detecting = False
        self.detectType = detectType
        self.model_list = model_list
        self.set_detector(self.detectType, self.model_list)

        self.is_decoding_finished = False

    def set_detector(self, detectType, model_list):
        if detectType == '目标检测':
            model_path = 'model/detect' + os.path.sep + model_list[0]
            self.detector = YoloDetector(model_path)
        elif detectType == '语义分割':
            model_path = 'model/seg' + os.path.sep + model_list[0]
            self.detector = Segment(model_path)
        elif detectType == '姿态识别':
            model_path1 = 'model/detect' + os.path.sep + model_list[0]
            model_path2 = 'model/pose' + os.path.sep + model_list[1]
            self.detector = PoseDetect(model_path1, model_path2)
        self.detecting = True
    
    def set_frame_buffer(self, frame_buffer):
        self.frame_buffer = frame_buffer

    def get_detectType(self):
        return self.detectType
    
    def get_model_list(self):
        return self.model_list
    
    def set_detecting_status(self, status):
        self.detecting = status

    def decoding_finished(self):
        print('decoding_finished')
        self.is_decoding_finished = True

    def run(self):
        start_time = time.time()
        frame_count = 0
        fps=0
        while self.detecting:
            # 如果帧缓冲区中有帧，则取出一帧进行处理
            frame = self.frame_buffer.get_frame()
            
            if frame is not None:
                result = self.detector.detect(frame)

                end_time = time.time()
                frame_count += 1
                if end_time - start_time > 1:
                    fps = frame_count / (end_time - start_time)              
                    start_time = time.time()
                    frame_count = 0
                cv2.putText(result, "FPS: {:.2f}".format(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                self.result.emit(result)
            if self.frame_buffer.get_buffer_length() == 0 and self.is_decoding_finished:
                print('视频处理结束')
                self.detecting = False