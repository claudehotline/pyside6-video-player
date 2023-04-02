import cv2
from PySide6.QtCore import QObject, Signal, QThread
import numpy as np
from .VideoFrameProcessor import VideoFrameProcessor
from .OpencvVideoDecoder import OpencvVideoDecoder
from .FFmpegVideoDecoder import FFmpegVideoDecoder
from .FrameBuffer import FrameBuffer

class VideoPlayer(QObject):

    finished = Signal()
    progress_slider = Signal(int)
    image = Signal(np.ndarray)
    result = Signal(np.ndarray)
    start_detect = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.play = False
        self.frameBuffer = FrameBuffer()
        self.videoFrameReader = None
        self.videoFrameProcessor = None
        self.is_setting_done = False

        self.videoFrameReaderThread = QThread()
        self.videoFrameProcessorThread = QThread()

    def set_player(self, detectType, model_list, video_path):
        self.detectType = detectType
        self.model_list = model_list
        self.video_path = video_path
        
        if self.play != True:  
            self.set_videoFrameReader(self.video_path)
            self.set_videoFrameDetector(self.detectType, self.model_list)
        else:
            if self.video_path != self.videoFrameReader.get_video_path() and self.video_path != '':
                self.videoFrameReader.set_video_path(self.video_path)
            if self.detectType != self.videoFrameProcessor.get_detectType() or self.model_list != self.videoFrameProcessor.get_model_list():
                self.videoFrameProcessor.set_detector(self.detectType, self.model_list)

        self.is_setting_done = True

    def set_videoFrameReader(self, video_path):
        self.videoFrameReader = self.get_video_decoder(video_path)
        self.videoFrameReader.set_frame_buffer(self.frameBuffer)
        self.videoFrameReaderThread.started.connect(self.videoFrameReader.run)
        self.videoFrameReader.moveToThread(self.videoFrameReaderThread)
        self.videoFrameReader.set_decoding_status(True)

    def set_videoFrameDetector(self, detectType, model_list):
        self.videoFrameProcessor = VideoFrameProcessor(detectType, model_list)
        self.videoFrameProcessor.set_frame_buffer(self.frameBuffer)
        self.videoFrameProcessorThread.started.connect(self.videoFrameProcessor.run)
        self.start_detect.connect(self.videoFrameProcessor.run)
        self.videoFrameProcessor.moveToThread(self.videoFrameProcessorThread)

    def set_frame(self, frame):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.total_frames * frame / 100))

    def set_play_status(self, status):
        if status == False:
            # self.videoFrameReader.set_decoding_status(False)
            self.videoFrameProcessor.set_detecting_status(False)
            self.play = status
        else:
            # self.videoFrameReader.set_decoding_status(True)
            self.videoFrameProcessor.set_detecting_status(True)
            self.start_detect.emit()
            self.play = status

    def get_setting_status(self):
        return self.is_setting_done

    def get_play_status(self):
        return self.play
    
    def get_video_frame_processor(self):
        return self.videoFrameProcessor
    
    def get_video_decoder(self, video_path):
        if video_path.startswith('rtsp://'):
            video_decoder = FFmpegVideoDecoder()
            video_decoder.set_video_path(video_path)
            return video_decoder
        else:
            video_decoder = OpencvVideoDecoder()
            video_decoder.set_video_path(video_path)
            return video_decoder

    def playVideo(self):
        print('playing')
        self.videoFrameProcessorThread.start()
        self.videoFrameReaderThread.start()
        self.play = True