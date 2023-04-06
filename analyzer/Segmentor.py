from mmdeploy_python import Segmentor
import numpy as np
# from analyzer import device

from mmdeploy.apis.utils import build_task_processor
from mmdeploy.utils import get_input_shape, load_config
import torch

class Segment():

    def __init__(self, model_path):
        # self.seg_detector = Segmentor(model_path, device, 0)

        self.deploy_cfg = 'I:/mmdeploy/configs/mmseg/segmentation_onnxruntime_dynamic.py'    
        # self.model_cfg = 'I:/pyside6/pyside6-video-player/pspnet_r18b-d8_4xb2-80k_cityscapes-512x1024.py'
        self.model_cfg = 'I:/mmsegmentation/configs/vit/vit_deit-b16_mln_upernet_8xb2-160k_ade20k-512x512.py'
        self.device = 'cpu'
        # self.backend_model = ['I:/pyside6/pyside6-video-player/model/seg/pspnet/end2end.onnx']
        self.backend_model = ['I:/pyside6/pyside6-video-player/model/seg/vit/end2end.onnx']


        # read deploy_cfg and model_cfg
        self.deploy_cfg, self.model_cfg = load_config(self.deploy_cfg, self.model_cfg)

        # build task and backend model
        self.task_processor = build_task_processor(self.model_cfg, self.deploy_cfg, self.device)
        self.model = self.task_processor.build_backend_model(self.backend_model)
    
    def detect(self, frame):
        # process input image
        input_shape = get_input_shape(self.deploy_cfg)
        self.model_inputs, _ = self.task_processor.create_input(frame, input_shape)
        # seg = self.seg_detector(frame)

        with torch.no_grad():
            result = self.model.test_step(self.model_inputs)

        image = result[0].pred_sem_seg.data.cpu().numpy()
        seg = np.squeeze(image, axis=0)

        if seg.dtype == np.float32:
            seg = np.argmax(seg, axis=0)

        palette = self.get_palette()


        color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)

        for label, color in enumerate(palette):
            if label == 12:
                color_seg[seg == label, :] = (0, 255, 0)
        # convert to BGR
        color_seg = color_seg[..., ::-1]

        frame = frame * 0.7 + color_seg * 0.3
        frame = frame.astype(np.uint8)

        return frame
    
    
    def get_palette(self, num_classes=256):
        # ade20k 数据集 标签 名字   0:background 1:road 2:sidewalk 3:building 4:wall 5:fence 6:pole 7:traffic light 8:traffic sign 9:vegetation 10:terrain 11:sky 12:person 13:rider 14:car 15:truck 16:bus 17:train 18:motorcycle 19:bicycle
        state = np.random.get_state()
        # random color
        np.random.seed(42)
        palette = np.random.randint(0, 256, size=(num_classes, 3))
        np.random.set_state(state)
        return [tuple(c) for c in palette]