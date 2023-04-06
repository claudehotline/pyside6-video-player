from mmdeploy.apis.utils import build_task_processor
from mmdeploy.utils import get_input_shape, load_config
import torch
import cv2
import numpy as np

deploy_cfg = 'I:/mmdeploy/configs/mmseg/segmentation_onnxruntime_dynamic.py'
model_cfg = './pspnet_r18b-d8_4xb2-80k_cityscapes-512x1024.py'
device = 'cpu'
backend_model = ['I:/pyside6/pyside6-video-player/model/seg/pspnet/end2end.onnx']
image = './cityscapes.png'

# read deploy_cfg and model_cfg
deploy_cfg, model_cfg = load_config(deploy_cfg, model_cfg)

# build task and backend model
task_processor = build_task_processor(model_cfg, deploy_cfg, device)
model = task_processor.build_backend_model(backend_model)

# process input image
input_shape = get_input_shape(deploy_cfg)
model_inputs, _ = task_processor.create_input(image, input_shape)

# do model inference
with torch.no_grad():
    print('infer')
    result = model.test_step(model_inputs)

# print(result[0])
# visualize results
# visualize results
task_processor.visualize(
    image=image,
    model=model,
    result=result[0],
    window_name='visualize',
    output_file='./output_segmentation.png')

result1 = result[0].pred_sem_seg.data.cpu().numpy()
retult2 = np.squeeze(result1, axis=0)
print(retult2.shape)

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

detector = Segmentor('I:/pyside6/pyside6-video-player/model/seg/pspnet', device, 0)

# image = cv2.imread('I:/pyside6/pyside6-video-player/test_frame.jpg')
image = cv2.imread('I:/pyside6/pyside6-video-player/cityscapes.png')
seg = detector(image)
print(seg.shape)

# 判断 result1 和 seg 中的元素是否相等
print(np.array_equal(result1, seg))