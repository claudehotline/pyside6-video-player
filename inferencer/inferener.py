import os
import numpy as np
import onnxruntime
# import tensorrt as trt
# import pycuda.driver as cuda
# import pycuda.autoinit

class inferencer:
  def __init__(self, model_path, device):
    self.device = device

    self.output = None

    if self.device == 'cpu':
      self.model = onnxruntime.InferenceSession(model_path+os.sep+'end2end.onnx')
    elif self.device == 'cuda':
      # trt_logger = trt.Logger(trt.Logger.INFO)
      # runtime = trt.Runtime(trt_logger)
      # with open(model_path+os.sep+'end2end.engine', "rb") as f:
      #   self.model = runtime.deserialize_cuda_engine(f.read())
      pass

  def infer(self, frame):
    if self.device == 'cpu':
      ort_inputs = {self.model.get_inputs()[0].name: to_numpy(frame)}
      ort_outs = self.model.run(None, ort_inputs)
      self.output = ort_outs[0][0]
    elif self.device == 'cuda':
      # context = self.model.create_execution_context()
      # INPUT_DATA_TYPE = np.float32
      # stream = cuda.Stream()
      # host_in = cuda.pagelocked_empty(trt.volume(self.model.get_binding_shape(0)), dtype=INPUT_DATA_TYPE)
      # host_out = cuda.pagelocked_empty(trt.volume(self.get_binding_shape(1)), dtype=INPUT_DATA_TYPE)
      # device_in = cuda.mem_alloc(host_in.nbytes)
      # device_out = cuda.mem_alloc(host_out.nbytes)
      # bindings = [int(device_in), int(device_out)]
      # np.copyto(host_in, frame.ravel())
      # cuda.memcpy_htod_async(device_in, host_in, stream)
      # context.execute_async_v2(bindings, stream.handle)
      # cuda.memcpy_dtoh_async(host_out, device_out, stream)
      # stream.synchronize()
      # self.output = host_out.reshape(201,18,4)
      pass
    return self.output


def to_numpy(tensor):
    return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()