from PySide6.QtCore import QObject, Signal, QThread, Slot
import numpy as np
import torch
from .VideoFrameProcessor import VideoFrameProcessor
from .OpencvVideoDecoder import OpencvVideoDecoder
from .FFmpegVideoDecoder import FFmpegVideoDecoder
from .FrameBuffer import FrameBuffer

class VideoPlayer(QObject):

    finished = Signal()
    progress_slider = Signal(int)
    image = Signal(np.ndarray)
    set_frame_num = Signal(int)
    start_detect = Signal()
    start_decode = Signal()
    update_progress_bar = Signal(int)
    stop = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.play = False
        self.frameBuffer = FrameBuffer()
        self.videoFrameReader = None
        self.videoFrameProcessor = None
        self.is_setting_done = False
        self.progress = 0

        self.videoFrameReaderThread = QThread()
        self.videoFrameProcessorThread = QThread()

    @Slot(str, list, str)
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
                self.frameBuffer.clear_buffer()
                if self.videoFrameReader.get_decoding_status() == False:
                    self.videoFrameReader.set_decoding_status(True)
                    self.start_decode.emit()
                if self.videoFrameProcessor.detecting == False:
                    self.videoFrameProcessor.detecting = True
                    self.start_detect.emit()
            if self.detectType != self.videoFrameProcessor.get_detectType() or self.model_list != self.videoFrameProcessor.get_model_list():
                self.videoFrameProcessor.set_detector(self.detectType, self.model_list)

        self.is_setting_done = True

    def set_videoFrameReader(self, video_path):
        # 创建视频解码器
        self.videoFrameReader = self.get_video_decoder(video_path)
        self.videoFrameReader.set_frame_buffer(self.frameBuffer)
        # 设置解码器的信号槽
        self.videoFrameReaderThread.started.connect(self.videoFrameReader.run)
        self.start_decode.connect(self.videoFrameReader.run)
        # 设置解码器线程
        self.videoFrameReader.moveToThread(self.videoFrameReaderThread)
        # 设置解码器解码状态
        self.videoFrameReader.set_decoding_status(True)

    def set_videoFrameDetector(self, detectType, model_list):
        # 创建视频检测器
        self.videoFrameProcessor = VideoFrameProcessor(detectType, model_list)
        self.videoFrameProcessor.set_frame_buffer(self.frameBuffer)
        # 设置检测器的信号槽
        self.videoFrameProcessorThread.started.connect(self.videoFrameProcessor.run)
        self.start_detect.connect(self.videoFrameProcessor.run)
        self.videoFrameProcessor.update_progress.connect(lambda x: self.update_progress(x))
        self.set_frame_num.connect(lambda x:self.videoFrameProcessor.set_frame_num(x))
        self.videoFrameReader.decoding_finished.connect(self.send_decoding_finished_to_process)
        self.videoFrameProcessor.start_decoding.connect(self.start_decoding)
        # 设置检测器线程
        self.videoFrameProcessor.moveToThread(self.videoFrameProcessorThread)

    def set_frame(self, frame):
        '''
        设置视频播放的帧数
        '''

        # 解码器停止解码，清空缓冲区，检测器停止检测
        self.videoFrameReader.set_decoding_status(False)
        self.frameBuffer.clear_buffer()
        self.videoFrameProcessor.set_detecting_status(False)
        # 根据进度条进度设置解码器和检测器的当前帧数
        self.videoFrameReader.set_frame(int(self.videoFrameReader.get_video_total_frames() * frame / 100))
        self.videoFrameProcessor.set_current_frame(int(self.videoFrameReader.get_video_total_frames() * frame / 100))
        # 设置解码器和检测器的运行状态
        self.videoFrameReader.set_decoding_status(True)
        self.videoFrameProcessor.set_detecting_status(True)
        # 设置解码状态为未完成
        self.videoFrameProcessor.set_is_finished(False)
        self.start_decode.emit()
        self.start_detect.emit()
        self.play = True

    def set_processor_score_threshold(self, score_threshold):
        self.videoFrameProcessor.set_detector_score_threshold(score_threshold)

    @Slot()
    def update_progress(self, frame_num):
        self.progress = int(frame_num / self.videoFrameReader.get_video_total_frames() * 100)
        self.update_progress_bar.emit(self.progress)

    def set_play_status(self, status):
        '''
            设置播放状态的播放和暂停状态
        '''
        
        if status == False:
            self.videoFrameProcessor.set_detecting_status(False)
            self.play = status
        else:
            self.videoFrameProcessor.set_detecting_status(True)
            self.start_detect.emit()
            self.play = status

    def get_setting_status(self):
        return self.is_setting_done
    
    def set_setting_status(self, status):
        self.is_setting_done = status

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

    @Slot()
    def start_decoding(self):
        self.videoFrameReader.set_decoding_status(True)
        self.start_decode.emit()

    @Slot()
    def send_decoding_finished_to_process(self):
        self.videoFrameProcessor.decoding_finished()

    @Slot()
    def playVideo(self):
        print('playing')
        self.videoFrameProcessorThread.start()
        self.videoFrameReaderThread.start()
        self.play = True

    @Slot()
    def release(self):
        self.play = False
        if self.videoFrameReaderThread.isRunning():
            self.videoFrameReader.set_decoding_status(False)
            self.videoFrameReaderThread.quit()
            self.videoFrameReaderThread.wait()
            self.videoFrameReader.cap.release()
        self.frameBuffer.clear_buffer()      
        if self.videoFrameProcessorThread.isRunning():
            self.videoFrameProcessor.set_detecting_status(False)
            self.videoFrameProcessorThread.quit()
            self.videoFrameProcessorThread.wait()
        self.stop.emit()
