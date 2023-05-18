from lib.test.tracker.basetracker import BaseTracker
import torch
from lib.train.data.processing_utils import sample_target
# for debug
import cv2
import os
from lib.utils.merge import merge_template_search
from lib.models.stark import build_starks
from lib.test.tracker.stark_utils import Preprocessor
from lib.test.tracker.stark_utils import Preprocessor_onnx
from lib.utils.box_ops import clip_box
import onnxruntime


class STARK_S_onnx(BaseTracker):
    def __init__(self, id):
        super(STARK_S_onnx, self).__init__()
        """build two sessions"""
        '''2021.7.5 Add multiple gpu support'''
        providers = ["CPUExecutionProvider"]
        self.ort_sess_z = onnxruntime.InferenceSession("model/tracking/stark/stark_s_backbone_bottleneck_pe.onnx", providers=providers)
        self.ort_sess_x = onnxruntime.InferenceSession("model/tracking/stark/stark_s_complete.onnx", providers=providers)
        self.preprocessor = Preprocessor_onnx()
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

class STARK_S(BaseTracker):
    def __init__(self, params):
        super(STARK_S, self).__init__()
        network = build_starks(params.cfg)
        network.load_state_dict(torch.load(params.checkpoint, map_location='cpu')['net'], strict=True)
        self.cfg = params.cfg
        # self.network = network.cuda()
        self.network = network
        self.network.eval()
        self.preprocessor = Preprocessor()
        self.state = None
        self.center_pos = []
        # for debug
        self.debug = False
        self.frame_id = 0
        if self.debug:
            self.save_dir = "debug"
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
        # for save boxes from all queries
        self.save_all_boxes = params.save_all_boxes
        self.z_dict1 = {}

    def initialize(self, image, info: dict):
        # forward the template once
        TEMPLATE_FACTOR=2.0
        TEMPLATE_SIZE=128
        z_patch_arr, _, z_amask_arr = sample_target(image, info['init_bbox'], TEMPLATE_FACTOR,
                                                    output_sz=TEMPLATE_SIZE)
        template = self.preprocessor.process(z_patch_arr, z_amask_arr)
        with torch.no_grad():
            self.z_dict1 = self.network.forward_backbone(template)
        # save states
        self.state = info['init_bbox']
        self.center_pos.append((self.state[0] + self.state[2] / 2, self.state[1] + self.state[3] / 2))
        self.frame_id = 1
        if self.save_all_boxes:
            '''save all predicted boxes'''
            all_boxes_save = info['init_bbox'] * self.cfg.MODEL.NUM_OBJECT_QUERIES
            return {"all_boxes": all_boxes_save}

    def track(self, image, info: dict = None):
        H, W, _ = image.shape
        self.frame_id += 1
        SEARCH_FACTOR = 5.0
        SEARCH_SIZE = 320
        x_patch_arr, resize_factor, x_amask_arr = sample_target(image, self.state, SEARCH_FACTOR,
                                                                output_sz=SEARCH_SIZE)  # (x1, y1, w, h)
        search = self.preprocessor.process(x_patch_arr, x_amask_arr)
        with torch.no_grad():
            x_dict = self.network.forward_backbone(search)
            # merge the template and the search
            feat_dict_list = [self.z_dict1, x_dict]
            seq_dict = merge_template_search(feat_dict_list)
            # run the transformer
            out_dict, _, _ = self.network.forward_transformer(seq_dict=seq_dict, run_box_head=True)

        print("out_dict: ", out_dict)

        pred_boxes = out_dict['pred_boxes'].view(-1, 4)
        # Baseline: Take the mean of all pred boxes as the final result
        pred_box = (pred_boxes.mean(dim=0) * SEARCH_SIZE / resize_factor).tolist()  # (cx, cy, w, h) [0,1]
        # get the final box result
        self.state = clip_box(self.map_box_back(pred_box, resize_factor), H, W, margin=10)
        self.center_pos.append((self.state[0] + self.state[2] / 2, self.state[1] + self.state[3] / 2))

        # for debug
        if self.debug:
            x1, y1, w, h = self.state
            image_BGR = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.rectangle(image_BGR, (int(x1),int(y1)), (int(x1+w),int(y1+h)), color=(0,0,255), thickness=2)
            save_path = os.path.join(self.save_dir, "%04d.jpg" % self.frame_id)
            cv2.imwrite(save_path, image_BGR)
        if self.save_all_boxes:
            '''save all predictions'''
            all_boxes = self.map_box_back_batch(pred_boxes * SEARCH_SIZE / resize_factor, resize_factor)
            all_boxes_save = all_boxes.view(-1).tolist()  # (4N, )
            return {"target_bbox": self.state,
                    "all_boxes": all_boxes_save}
        else:
            return {"target_bbox": self.state}

    def map_box_back(self, pred_box: list, resize_factor: float):
        SEARCH_SIZE = 320
        cx_prev, cy_prev = self.state[0] + 0.5 * self.state[2], self.state[1] + 0.5 * self.state[3]
        cx, cy, w, h = pred_box
        half_side = 0.5 * SEARCH_SIZE / resize_factor
        cx_real = cx + (cx_prev - half_side)
        cy_real = cy + (cy_prev - half_side)
        return [cx_real - 0.5 * w, cy_real - 0.5 * h, w, h]

    def map_box_back_batch(self, pred_box: torch.Tensor, resize_factor: float):
        SEARCH_SIZE = 320
        cx_prev, cy_prev = self.state[0] + 0.5 * self.state[2], self.state[1] + 0.5 * self.state[3]
        cx, cy, w, h = pred_box.unbind(-1) # (N,4) --> (N,)
        half_side = 0.5 * SEARCH_SIZE / resize_factor
        cx_real = cx + (cx_prev - half_side)
        cy_real = cy + (cy_prev - half_side)
        return torch.stack([cx_real - 0.5 * w, cy_real - 0.5 * h, w, h], dim=-1)
