from utils.starktrack.lib.test.tracker.basetracker import BaseTracker
import torch
from utils.starktrack.lib.train.data.processing_utils import sample_target
# for debug
import cv2
import os
from utils.starktrack.lib.utils.box_ops import clip_box
# for onnxruntime
from utils.starktrack.lib.test.tracker.stark_utils import PreprocessorX_onnx
import onnxruntime


class STARK_LightningXtrt_onnx(BaseTracker):
    def __init__(self, id):
        super(STARK_LightningXtrt_onnx, self).__init__()
        """build two sessions"""
        '''2021.7.5 Add multiple gpu support'''
        providers = ["CPUExecutionProvider"]
        self.ort_sess_z = onnxruntime.InferenceSession("model/tracking/stark/backbone_bottleneck_pe.onnx", providers=providers)
        self.ort_sess_x = onnxruntime.InferenceSession("model/tracking/stark/complete.onnx", providers=providers)
        self.preprocessor = PreprocessorX_onnx()
        self.state = None
        # for debug
        # self.debug = False
        self.frame_id = 0
        self.track_id = id
        # if self.debug:
        #     self.save_dir = "debug"
        #     if not os.path.exists(self.save_dir):
        #         os.makedirs(self.save_dir)
        self.ort_outs_z = []
        self.center_pos = []

    def initialize(self, image, info: dict):
        template_factor = 2.0
        template_size = 128
        z_patch_arr, _, z_amask_arr = sample_target(image, info['init_bbox'], template_factor,
                                                    output_sz=template_size)
        
        template, template_mask = self.preprocessor.process(z_patch_arr, z_amask_arr)
        # forward the template once
        ort_inputs = {'img_z': template, 'mask_z': template_mask}
        self.ort_outs_z = self.ort_sess_z.run(None, ort_inputs)

        # save states
        self.state = info['init_bbox']

        self.center_pos.append([self.state[0] + 0.5 * self.state[2], self.state[1] + 0.5 * self.state[3]])
        # self.frame_id = 0
        self.frame_id = 1

    def track(self, image):
        H, W, _ = image.shape
        self.frame_id += 1
        search_factor = 5.0
        search_size = 320
        x_patch_arr, resize_factor, x_amask_arr = sample_target(image, self.state, search_factor,
                                                                output_sz=search_size)  # (x1, y1, w, h)
        search, search_mask = self.preprocessor.process(x_patch_arr, x_amask_arr)

        ort_inputs = {'img_x': search,
                      'mask_x': search_mask,
                      'feat_vec_z': self.ort_outs_z[0],
                      'mask_vec_z': self.ort_outs_z[1],
                      'pos_vec_z': self.ort_outs_z[2],
                      }

        ort_outs = self.ort_sess_x.run(None, ort_inputs)

        pred_box = (ort_outs[0].reshape(4) * search_size / resize_factor).tolist()  # (cx, cy, w, h) [0,1]
        # get the final box result
        self.state = clip_box(self.map_box_back(pred_box, resize_factor), H, W, margin=10)

        self.center_pos.append([self.state[0] + 0.5 * self.state[2], self.state[1] + 0.5 * self.state[3]])
        # for debug
        # if self.debug:
        #     x1, y1, w, h = self.state
        #     image_BGR = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        #     cv2.rectangle(image_BGR, (int(x1), int(y1)), (int(x1 + w), int(y1 + h)), color=(0, 0, 255), thickness=2)
        #     save_path = os.path.join(self.save_dir, "%04d.jpg" % self.frame_id)
        #     cv2.imwrite(save_path, image_BGR)
        return {"target_bbox": self.state}

    def map_box_back(self, pred_box: list, resize_factor: float):
        search_size = 320
        cx_prev, cy_prev = self.state[0] + 0.5 * self.state[2], self.state[1] + 0.5 * self.state[3]
        cx, cy, w, h = pred_box
        half_side = 0.5 * search_size / resize_factor
        cx_real = cx + (cx_prev - half_side)
        cy_real = cy + (cy_prev - half_side)
        return [cx_real - 0.5 * w, cy_real - 0.5 * h, w, h]
