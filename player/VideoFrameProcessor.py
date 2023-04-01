from PySide6.QtCore import QObject, Signal
import numpy as np
import time
import cv2

class VideoFrameProcessor(QObject):
    
    result = Signal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.detector = None


    def set_detector(self, detector):
        self.detector = detector
    
    def set_frame_buffer(self, frame_buffer):
        self.frame_buffer = frame_buffer

    def run(self):
        start_time = time.time()
        frame_count = 0
        fps=0
        while True:
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