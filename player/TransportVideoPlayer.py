from PySide6.QtCore import Signal, Slot
from .VideoFrameProcessor import VideoFrameProcessor
from .VideoPlayer import VideoPlayer

class TransportVideoPlayer(VideoPlayer):

    send_car_count = Signal(int, int)

    def __init__(self):
        super().__init__()


    def set_videoFrameDetector(self, detectType, model_list):
        # 创建视频检测器
        print('set_TransportvideoFrameDetector')
        self.videoFrameProcessor = VideoFrameProcessor(detectType, model_list)
        self.videoFrameProcessor.set_frame_buffer(self.frameBuffer)
        # 设置检测器的信号槽
        self.videoFrameProcessorThread.started.connect(self.videoFrameProcessor.run)
        self.start_detect.connect(self.videoFrameProcessor.run)
        self.videoFrameProcessor.update_progress.connect(lambda x: self.update_progress(x))
        self.set_frame_num.connect(lambda x:self.videoFrameProcessor.set_frame_num(x))
        self.videoFrameReader.decoding_finished.connect(self.send_decoding_finished_to_process)
        self.videoFrameProcessor.start_decoding.connect(self.start_decoding)
        self.videoFrameProcessor.detector.car_count.connect(lambda up, down: self.update_car_count(up, down))
        # 设置检测器线程
        self.videoFrameProcessor.moveToThread(self.videoFrameProcessorThread)

    @Slot(int, int)
    def update_car_count(self, up_count, down_count):
        self.up_count = up_count
        self.down_count = down_count
        # print('up_count: ', up_count, 'down_count: ', down_count)
        self.send_car_count.emit(self.up_count, self.down_count)