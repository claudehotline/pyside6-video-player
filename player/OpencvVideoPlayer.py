import cv2
from PySide6.QtCore import QObject, Signal
import numpy as np
import time

class OpencvVideoPlayer(QObject):

    finished = Signal()
    progress_slider = Signal(int)
    image = Signal(np.ndarray)
    result = Signal(np.ndarray)

    def __init__(self):
        QObject.__init__(self)
        self.play = False


    def set_video(self, video_path):
        # 创建 VideoCapture 对象并指定要读取的视频文件路径
        self.cap = cv2.VideoCapture(video_path)
        # 获取视频的帧率、宽度和高度
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 获取self.cap的总帧数
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def set_detector(self, detector):
        self.detector = detector

    def set_frame(self, frame):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.total_frames * frame / 100))

    def set_play_status(self, status):
        self.play = status

    def get_play_status(self):
        return self.play

    def playVideo(self):
        start_time = time.time()
        count = 0
        fps = 0
        while self.play:
            start_detect = time.time()
            ret, frame = self.cap.read()

            if not ret:
                break

            frame_copy = frame.copy()
            # 在frame_copy上绘制self.fps, self.width, self.height, self.total_frames
            cv2.putText(frame_copy, 'FPS: {}'.format(self.fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame_copy, 'Width: {}'.format(self.width), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame_copy, 'Height: {}'.format(self.height), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame_copy, 'Total Frames: {}'.format(self.total_frames), (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.progress_slider.emit(int(pos/self.total_frames*100))

            
            result = self.detector.detect(frame)
            

            count += 1
            end_time = time.time()
            if end_time - start_time >= 1:
                fps = count
                count = 0
                start_time = time.time()

            cv2.putText(result, 'FPS: {}'.format(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            self.image.emit(frame_copy)
            self.result.emit(result)

            end_detect = time.time()
            detect_time = end_detect - start_detect
            # opencv 帧率控制
            cv2.waitKey(int(1000/self.fps - detect_time*1000))