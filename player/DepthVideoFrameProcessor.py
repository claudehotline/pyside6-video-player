from PySide6.QtCore import Signal, Slot
from player.VideoFrameProcessor import VideoFrameProcessor
from analyzer.DepthEstimator import DepthEstimator
import time
import numpy as np
import cv2

class DepthVideoFrameProcessor(VideoFrameProcessor):
    
    frame = Signal(np.ndarray)
    
    def __init__(self, detectType, model_list):
        super(DepthVideoFrameProcessor, self).__init__(detectType, model_list)

    def set_detector(self, detectType, model_list):
        model_path = 'model\depth\manydepth\KITTI_MR'
        self.detector = DepthEstimator(model_path)
        self.detecting = True

    @Slot()
    def run(self):
        start_time = time.time()
        frame_count = 0
        fps=0
        print('start run')
        while self.detecting:
            start_detect_time = time.time()
            # 如果帧缓冲区中有帧，则取出一帧进行处理
            frame = self.frame_buffer.get_frame()
            print('frame shape: ', frame.shape)
            if self.frame_buffer.get_buffer_length() < 100:
                self.start_decoding.emit()
            if frame is not None:
                print('detecting')
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
                
                self.result.emit(result)
                self.frame.emit(frame)
            if self.frame_buffer.get_buffer_length() == 0 and self.is_decoding_finished:
                print('视频处理结束')
                self.detecting = False
            end_detect_time = time.time()
            detect_time=end_detect_time-start_detect_time
            # 使用time.sleep 控制帧速为25帧/s   1/25=0.04s
            if detect_time < 0.033:
                time.sleep(0.033 - detect_time)