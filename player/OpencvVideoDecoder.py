import cv2
from PySide6.QtCore import QObject

class OpencvVideoDecoder(QObject):

  def __init__(self):
    super().__init__()
    self.stream = None
    self.frame_buffer = None
    self.cap = None


  def set_frame_buffer(self, frame_buffer):
    self.frame_buffer = frame_buffer


  def set_video_path(self, stream):
    self.stream = stream
    self.cap = cv2.VideoCapture(self.stream)
    self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)


  def run(self):

    while True:
      ret, frame = self.cap.read()
      if not ret:
        break
      self.frame_buffer.add_frame(frame)
      print(self.frame_buffer.get_buffer_length())

    self.cap.release()