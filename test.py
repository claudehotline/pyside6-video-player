import os
import torch
import sys
import cv2
import numpy as np

device = 'cuda' if torch.cuda.is_available() else 'cpu'
if torch.cuda.is_available():
  os.add_dll_directory(
      'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/bin')
  os.add_dll_directory(
      'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/lib/x64')
  os.add_dll_directory('E:/Projects/deeplearning/mmlab/TensorRT-8.5.3.1/lib')
  os.add_dll_directory('H:/opencv/build/x64/vc16/bin')
else:
  sys.path.append('I:/mmdeploy/build/bin/Release')
  os.add_dll_directory('D:/opencv/build/x64/vc16/bin')
  os.add_dll_directory('D:/onnxruntime-win-x64-1.8.1/lib')


from mmdeploy_python import Segmentor

def get_palette(num_classes=256):
  state = np.random.get_state()
  # random color
  np.random.seed(42)
  palette = np.random.randint(0, 256, size=(num_classes, 3))
  np.random.set_state(state)
  return [tuple(c) for c in palette]

detector = Segmentor('I:/pyside6/pyside6-video-player/model/seg/vit', device, 0)

# image = cv2.imread('I:/pyside6/pyside6-video-player/test_frame.jpg')
image = cv2.imread('I:/pyside6/pyside6-video-player/cityscapes.png')

seg = detector(image)
print(seg)
palette = get_palette()
color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)

for label, color in enumerate(palette):
  # if label == 6:
    color_seg[seg == label, :] = color
    # convert to BGR
    color_seg = color_seg[..., ::-1]
    frame = image * 0.5 + color_seg * 0.5
    frame = frame.astype(np.uint8)

cv2.imshow('test_seg', frame)
cv2.waitKey(0)