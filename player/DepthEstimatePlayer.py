from .DepthVideoFrameProcessor import DepthVideoFrameProcessor
from .VideoPlayer import VideoPlayer

class DepthEstimatePlayer(VideoPlayer):

    def __init__(self):
        super().__init__()

    def set_videoFrameDetector(self, detectType, model_list):
        # 创建视频检测器
        print('set_videoFrameDetector')
        self.videoFrameProcessor = DepthVideoFrameProcessor(detectType, model_list)
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