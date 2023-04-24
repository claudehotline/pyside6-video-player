import os
import numpy as np
import onnxruntime
import pycuda.driver as cuda
import pycuda.autoinit
import tensorrt as trt

class inferencer:

  def __init__(self, model_path, device):
    print('init inferencer')
    self.device = device
    self.output = None

    if self.device == 'cpu':
      self.model = onnxruntime.InferenceSession(model_path+os.sep+'end2end.onnx')
    elif self.device == 'cuda':
      # cuda.init()
      self.cfx = cuda.Device(0).make_context()
      with open(model_path+os.sep+'end2end.engine', "rb") as f:
        engine_data = f.read()
      self.model = trt.Runtime(trt.Logger(trt.Logger.INFO)).deserialize_cuda_engine(engine_data)

      self.stream = cuda.Stream()

      INPUT_DATA_TYPE = np.float32
      self.host_in = cuda.pagelocked_empty(trt.volume(self.model.get_binding_shape(0)), dtype=INPUT_DATA_TYPE)
      self.host_out = cuda.pagelocked_empty(trt.volume(self.model.get_binding_shape(1)), dtype=INPUT_DATA_TYPE)
      self.device_in = cuda.mem_alloc(self.host_in.nbytes)
      self.device_out = cuda.mem_alloc(self.host_out.nbytes)
      self.bindings = [int(self.device_in), int(self.device_out)]

      self.context = self.model.create_execution_context()

  def __call__(self, frame):
    if self.device == 'cpu':
      ort_inputs = {self.model.get_inputs()[0].name: to_numpy(frame)}
      ort_outs = self.model.run(None, ort_inputs)
      self.output = ort_outs[0][0]
    elif self.device == 'cuda': 
      self.cfx.push()
      np.copyto(self.host_in, frame.ravel())
      cuda.memcpy_htod_async(self.device_in, self.host_in, self.stream)
      self.context.execute_async_v2(self.bindings, self.stream.handle)
      cuda.memcpy_dtoh_async(self.host_out, self.device_out, self.stream)
      self.stream.synchronize()
      self.output = self.host_out.reshape(201,18,4)
      self.cfx.pop()
    return self.output
  
  def __del__(self):
    print('del inferencer')
    if self.device == 'cuda':
      self.device_in.free()
      self.device_out.free()
      cuda.Context.pop()

def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()