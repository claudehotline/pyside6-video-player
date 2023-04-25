from PySide6.QtCore import QObject, Signal, Slot
import torch
import numpy as np
import time
import cv2
import os

from analyzer.YoloDetector import YoloDetector
from analyzer.Segmentor import Segment
from analyzer.PoseDetector import PoseDetect
# from analyzer.ActionAnalyzer import ActionAnalyzer
from analyzer.DeepLaneDetector import DeepLaneDetector
from analyzer.TrackingDetector import TrackingDetector

class VideoFrameProcessor(QObject):
    
    result = Signal(np.ndarray)
    update_progress = Signal(int)
    start_decoding = Signal()

    def __init__(self, detectType, model_list):
        super().__init__()

        self.detecting = False
        self.is_decoding_finished = False
        self.detector = None
        self.detectType = detectType
        self.model_list = model_list
        self.set_detector(self.detectType, self.model_list)
        self.current_frame = 0

    def set_detector(self, detectType, model_list):
        torch.cuda.empty_cache()
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
        elif detectType == '动作理解':
            # model_path = 'model/detect' + os.path.sep + model_list[0]
            # self.detector = ActionAnalyzer(model_path)
            # self.detector = DeepLaneDetector()
            self.detector = TrackingDetector()
        self.detecting = True

    def set_detector_score_threshold(self, score_threshold):
        self.detector.set_score_threshold(score_threshold)

    @Slot(int)
    def set_current_frame(self, current_frame):
        self.current_frame = current_frame
    
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

    def set_is_finished(self, status):
        self.is_decoding_finished = status

    @Slot()
    def run(self):
        start_time = time.time()
        frame_count = 0
        fps=0
        while self.detecting:
            start_detect_time = time.time()
            # 如果帧缓冲区中有帧，则取出一帧进行处理
            frame = self.frame_buffer.get_frame()
            if self.frame_buffer.get_buffer_length() < 100:
                self.start_decoding.emit()
            # print(self.frame_buffer.get_buffer_length(), self.is_decoding_finished)
            if frame is not None:
                # cv2.imwrite('test.jpg', frame)
                result = self.detector.detect(frame)
                self.current_frame = self.current_frame + 1
                self.update_progress.emit(self.current_frame)
                end_time = time.time()
                frame_count += 1
                if end_time - start_time > 1:
                    fps = round(frame_count / (end_time - start_time), 0)         
                    start_time = time.time()
                    frame_count = 0
                    
                cv2.putText(result, "FPS: {:.2f}".format(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # print('emit result')
                self.result.emit(result)
            if self.frame_buffer.get_buffer_length() == 0 and self.is_decoding_finished:
                print('视频处理结束')
                self.detecting = False
            end_detect_time = time.time()
            detect_time=end_detect_time-start_detect_time
            # print('detect_time:', detect_time)
            # 使用time.sleep 控制帧速为25帧/s   1/25=0.04s
            if detect_time < 0.033:
                time.sleep(0.033 - detect_time)