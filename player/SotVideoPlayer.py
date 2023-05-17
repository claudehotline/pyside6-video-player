from PySide6.QtCore import Signal, Slot
from .VideoFrameProcessor import VideoFrameProcessor
from .VideoPlayer import VideoPlayer

class SotVideoPlayer(VideoPlayer):


    def __init__(self):
        super().__init__()


    @Slot()
    def start_tracking(self):
        self.videoFrameProcessor.detector.start_tracking()

    @Slot()
    def stop_tracking(self):
        self.videoFrameProcessor.detector.stop_tracking()

    @Slot()
    def add_target(self):
        self.videoFrameProcessor.detector.add_tracker()