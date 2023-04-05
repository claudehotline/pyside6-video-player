import cv2
from mmdeploy_python import Restorer
from analyzer import device

class EsrganAnalyzer:

  def __init__(self, model_path):
    self.detector = Restorer(model_path, device, 0)

  def detect(self, frame):
    result = self.detector(frame)
    # convert to BGR
    # result = result[..., ::-1]
    cv2.imshow('result', result)

    return result  
