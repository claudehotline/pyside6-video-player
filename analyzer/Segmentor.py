from mmdeploy_python import Segmentor
import numpy as np
from analyzer import device

class Segment():

    def __init__(self, model_path):
        self.seg_detector = Segmentor(model_path, device, 0)
    
    def detect(self, frame):
        seg = self.seg_detector(frame)

        if seg.dtype == np.float32:
            seg = np.argmax(seg, axis=0)

        palette = self.get_palette()

        color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)
        for label, color in enumerate(palette):
            color_seg[seg == label, :] = color
        # convert to BGR
        color_seg = color_seg[..., ::-1]

        frame = frame * 0.5 + color_seg * 0.5
        frame = frame.astype(np.uint8)

        return frame
    
    
    def get_palette(self, num_classes=256):
        state = np.random.get_state()
        # random color
        np.random.seed(42)
        palette = np.random.randint(0, 256, size=(num_classes, 3))
        np.random.set_state(state)
        return [tuple(c) for c in palette]