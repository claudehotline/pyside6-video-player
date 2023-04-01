import cv2
import numpy as np
import os
import ffmpeg
from PySide6.QtCore import QObject

# 添加Path系统变量
os.environ['PATH'] = os.environ['PATH'] + ';H:/ffmpeg/bin'

class FFmpegVideoDecoder(QObject):

  def __init__(self):
    super().__init__()
    self.stream = None
    self.frame_buffer = None

  def set_frame_buffer(self, frame_buffer):
    self.frame_buffer = frame_buffer

  def set_video_path(self, stream):
    self.stream = stream

  def run(self):
    probe = ffmpeg.probe(self.stream)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = video_info['width']
    height = video_info['height']
    # 获取视频格式
    pixel_format = video_info['pix_fmt']
    # 获取format
    codec_name = video_info['codec_name']
        
    # 调用FFmpeg程序并将视频解码为YUV格式
    process = (
      ffmpeg
      .input(self.stream, codec=codec_name, pix_fmt=pixel_format, s='{}x{}'.format(width, height))
      .output('pipe:', format='rawvideo', pix_fmt=pixel_format)
      .run_async(pipe_stdout=True)
    )
        
    while True:
      in_bytes = process.stdout.read(width*height*3//2)

      if not in_bytes:
        break

      frame = np.frombuffer(in_bytes, np.uint8)
      frame = frame.reshape((height*3//2, width))
      frame = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_I420)
      self.frame_buffer.add_frame(frame)

    process.stdout.close()
    process.wait()