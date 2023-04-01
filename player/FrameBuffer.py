from PySide6.QtCore  import  QObject, Signal

# 定义一个帧缓冲区类，用于存储视频帧
class FrameBuffer(QObject):
    frame_received = Signal(object)

    def __init__(self):
        super().__init__()
        self._buffer = []

    def add_frame(self, frame):
        self._buffer.append(frame)
        self.frame_received.emit(frame)

    def get_frame(self):
        if len(self._buffer) > 0:
            return self._buffer.pop(0)
        else:
            return None
        
    def get_buffer_length(self):
        return len(self._buffer)