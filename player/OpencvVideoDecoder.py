import cv2
from PySide6.QtCore import QObject
from PySide6.QtCore import Signal, Slot

class OpencvVideoDecoder(QObject):

  decoding_finished = Signal()

  def __init__(self):
    super().__init__()
    self.stream = None
    self.frame_buffer = None
    self.cap = None
    self.decoding = False


  def set_frame_buffer(self, frame_buffer):
    self.frame_buffer = frame_buffer


  def set_video_path(self, stream):
    self.stream = stream
    self.cap = cv2.VideoCapture(self.stream)
    self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
    self.total_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)

  def get_video_total_frames(self):
    return self.total_frames

  def set_frame(self, frame_num):
    self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

  def get_video_path(self):
    return self.stream

  def set_decoding_status(self, status):
    self.decoding = status

  def set_pause_status(self, status):
    self.pause = status

  @Slot()
  def run(self):

    while self.decoding:

      ret, frame = self.cap.read()
      if not ret:
        break
      self.frame_buffer.add_frame(frame)
      
      # cv2.waitKey(int(1000 / 40))
    print('decoder stop')
    self.decoding_finished.emit()