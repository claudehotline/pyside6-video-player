import os
import torch
import sys

# import torch.hub
# torch.hub.set_dir('/path/to/new_cache/torch/hub')

device = 'cuda' if torch.cuda.is_available() else 'cpu'
if torch.cuda.is_available():
  sys.path.append('D:/Projects/deeplearning/mmlab/mmdeploy/build/bin/Release')
  os.add_dll_directory(
      'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/bin')
  os.add_dll_directory(
      'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/lib/x64')
  os.add_dll_directory('D:/Projects/deeplearning/mmlab/TensorRT-8.5.3.1/lib')
  os.add_dll_directory('D:/Projects/deeplearning/mmlab/onnxruntime-win-x64-gpu-1.14.1/lib')
  os.add_dll_directory('H:/opencv/build/x64/vc16/bin')
else:
  sys.path.append('I:/mmdeploy/build/bin/Release')
  os.add_dll_directory('D:/opencv/build/x64/vc16/bin')
  os.add_dll_directory('D:/onnxruntime-win-x64-1.8.1/lib')