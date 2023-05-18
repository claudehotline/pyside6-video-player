from lib.test.tracker.basetracker import BaseTracker
import torch
from lib.train.data.processing_utils import sample_target
from copy import deepcopy
# for debug
import cv2
import os
from lib.utils.merge import merge_template_search
from lib.models.stark import build_starkst
from lib.test.tracker.stark_utils import Preprocessor
from lib.test.tracker.stark_utils import Preprocessor_onnx
from lib.utils.box_ops import clip_box
import onnxruntime
import numpy as np


class STARK_ST_onnx(BaseTracker):
    def __init__(self, id):
        super(STARK_ST_onnx, self).__init__()
        """build two sessions"""
        '''2021.7.5 Add multiple gpu support'''
        providers = ["CPUExecutionProvider"]
        self.ort_sess_z = onnxruntime.InferenceSession("model/tracking/stark/stark_st1_backbone_bottleneck_pe.onnx", providers=providers)
        self.ort_sess_x = onnxruntime.InferenceSession("model/tracking/stark/stark_st1_complete.onnx", providers=providers)
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
        self.ort_outs_z = {}
        self.ort_outs_z_list = []
        self.center_pos = []
        self.num_extra_template = 1

    def initialize(self, image, info: dict):
        template_factor = 2.0
        template_size = 128
        z_patch_arr, _, z_amask_arr = sample_target(image, info['init_bbox'], template_factor,
                                                    output_sz=template_size)
        # cv2.imwrite('z_patch_init_arr.jpg', z_patch_arr)
        template, template_mask = self.preprocessor.process(z_patch_arr, z_amask_arr)
        # forward the template once
        ort_inputs = {'img_z': template, 'mask_z': template_mask}
        self.ort_outs_z = self.ort_sess_z.run(None, ort_inputs)

        for i in range(self.num_extra_template):
            self.ort_outs_z_list.append(deepcopy(self.ort_outs_z))

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

        feat_vec_z_list = []
        mask_vec_z_list = []
        pos_vec_z_list = []

        for i in range(self.num_extra_template):
            feat_vec_z_list.append(self.ort_outs_z_list[i][0])
            mask_vec_z_list.append(self.ort_outs_z_list[i][1])
            pos_vec_z_list.append(self.ort_outs_z_list[i][2])

        ort_inputs = {'img_x': search,
                      'mask_x': search_mask,
                      'feat_vec_z_list': np.array(feat_vec_z_list),
                      'mask_vec_z_list': np.array(mask_vec_z_list),
                      'pos_vec_z_list': np.array(pos_vec_z_list),
                      }

        ort_outs = self.ort_sess_x.run(None, ort_inputs)
        # print('ort_out: ', ort_outs)
        pred_box = (ort_outs[0].reshape(4) * search_size / resize_factor).tolist()  # (cx, cy, w, h) [0,1]
        # print('pred_box: ', pred_box)
        self.state = clip_box(self.map_box_back(pred_box, resize_factor), H, W, margin=10)
        # self.state = pred_box      
        # print('state: ', self.state)
        conf_score = ort_outs[1].tolist()[0]
        # print('conf_score: ', conf_score)
        template_factor = 2.0
        template_size = 128
        for idx, update_i in enumerate([30]):
            print('frame_id = ', self.frame_id)
            if self.frame_id % update_i == 0 and conf_score > 0.5:
                print('update template')
                z_patch_arr, _, z_amask_arr = sample_target(image, self.state, template_factor,
                                                    output_sz=template_size)
                # cv2.imwrite('z_patch_arr.jpg', z_patch_arr)
                template_t = self.preprocessor.process(z_patch_arr, z_amask_arr)
                ort_inputs = {'img_z': template_t, 'mask_z': z_amask_arr}
                self.ort_outs_z_list[idx+1] = self.ort_sess_z.run(None, ort_inputs)

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

class STARK_ST(BaseTracker):
    def __init__(self, params, dataset_name):
        super(STARK_ST, self).__init__(params)
        network = build_starkst(params.cfg)
        network.load_state_dict(torch.load(self.params.checkpoint, map_location='cpu')['net'], strict=True)
        self.cfg = params.cfg
        self.network = network.cuda()
        self.network.eval()
        self.preprocessor = Preprocessor()
        self.state = None
        # for debug
        self.debug = False
        self.frame_id = 0
        if self.debug:
            self.save_dir = "debug"
            if not os.path.exists(self.save_dir):
                os.makedirs(self.save_dir)
        # for save boxes from all queries
        self.save_all_boxes = params.save_all_boxes
        # template update
        self.z_dict1 = {}
        self.z_dict_list = []
        # Set the update interval
        DATASET_NAME = dataset_name.upper()
        if hasattr(self.cfg.TEST.UPDATE_INTERVALS, DATASET_NAME):
            self.update_intervals = self.cfg.TEST.UPDATE_INTERVALS[DATASET_NAME]
        else:
            self.update_intervals = self.cfg.DATA.MAX_SAMPLE_INTERVAL
        print("Update interval is: ", self.update_intervals)
        self.num_extra_template = len(self.update_intervals)

    def initialize(self, image, info: dict):
        # initialize z_dict_list
        self.z_dict_list = []
        # get the 1st template
        z_patch_arr1, _, z_amask_arr1 = sample_target(image, info['init_bbox'], self.params.template_factor,
                                                      output_sz=self.params.template_size)
        template1 = self.preprocessor.process(z_patch_arr1, z_amask_arr1)
        with torch.no_grad():
            self.z_dict1 = self.network.forward_backbone(template1)
        # get the complete z_dict_list
        self.z_dict_list.append(self.z_dict1)
        for i in range(self.num_extra_template):
            self.z_dict_list.append(deepcopy(self.z_dict1))

        # save states
        self.state = info['init_bbox']
        self.frame_id = 0
        if self.save_all_boxes:
            '''save all predicted boxes'''
            all_boxes_save = info['init_bbox'] * self.cfg.MODEL.NUM_OBJECT_QUERIES
            return {"all_boxes": all_boxes_save}

    def track(self, image, info: dict = None):
        H, W, _ = image.shape
        self.frame_id += 1
        # get the t-th search region
        x_patch_arr, resize_factor, x_amask_arr = sample_target(image, self.state, self.params.search_factor,
                                                                output_sz=self.params.search_size)  # (x1, y1, w, h)
        search = self.preprocessor.process(x_patch_arr, x_amask_arr)
        with torch.no_grad():
            x_dict = self.network.forward_backbone(search)
            # merge the template and the search
            feat_dict_list = self.z_dict_list + [x_dict]
            seq_dict = merge_template_search(feat_dict_list)
            # run the transformer
            out_dict, _, _ = self.network.forward_transformer(seq_dict=seq_dict, run_box_head=True, run_cls_head=True)
        # get the final result
        pred_boxes = out_dict['pred_boxes'].view(-1, 4)
        # Baseline: Take the mean of all pred boxes as the final result
        pred_box = (pred_boxes.mean(dim=0) * self.params.search_size / resize_factor).tolist()  # (cx, cy, w, h) [0,1]
        # get the final box result
        self.state = clip_box(self.map_box_back(pred_box, resize_factor), H, W, margin=10)
        # get confidence score (whether the search region is reliable)
        conf_score = out_dict["pred_logits"].view(-1).sigmoid().item()
        # update template
        for idx, update_i in enumerate(self.update_intervals):
            if self.frame_id % update_i == 0 and conf_score > 0.5:
                z_patch_arr, _, z_amask_arr = sample_target(image, self.state, self.params.template_factor,
                                                            output_sz=self.params.template_size)  # (x1, y1, w, h)
                template_t = self.preprocessor.process(z_patch_arr, z_amask_arr)
                with torch.no_grad():
                    z_dict_t = self.network.forward_backbone(template_t)
                self.z_dict_list[idx+1] = z_dict_t  # the 1st element of z_dict_list is template from the 1st frame

        # for debug
        if self.debug:
            x1, y1, w, h = self.state
            image_BGR = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.rectangle(image_BGR, (int(x1),int(y1)), (int(x1+w),int(y1+h)), color=(0,0,255), thickness=2)
            save_path = os.path.join(self.save_dir, "%04d.jpg" % self.frame_id)
            cv2.imwrite(save_path, image_BGR)
        if self.save_all_boxes:
            '''save all predictions'''
            all_boxes = self.map_box_back_batch(pred_boxes * self.params.search_size / resize_factor, resize_factor)
            all_boxes_save = all_boxes.view(-1).tolist()  # (4N, )
            return {"target_bbox": self.state,
                    "all_boxes": all_boxes_save,
                    "conf_score": conf_score}
        else:
            return {"target_bbox": self.state,
                    "conf_score": conf_score}

    def map_box_back(self, pred_box: list, resize_factor: float):
        cx_prev, cy_prev = self.state[0] + 0.5 * self.state[2], self.state[1] + 0.5 * self.state[3]
        cx, cy, w, h = pred_box
        half_side = 0.5 * self.params.search_size / resize_factor
        cx_real = cx + (cx_prev - half_side)
        cy_real = cy + (cy_prev - half_side)
        return [cx_real - 0.5 * w, cy_real - 0.5 * h, w, h]

    def map_box_back_batch(self, pred_box: torch.Tensor, resize_factor: float):
        cx_prev, cy_prev = self.state[0] + 0.5 * self.state[2], self.state[1] + 0.5 * self.state[3]
        cx, cy, w, h = pred_box.unbind(-1) # (N,4) --> (N,)
        half_side = 0.5 * self.params.search_size / resize_factor
        cx_real = cx + (cx_prev - half_side)
        cy_real = cy + (cy_prev - half_side)
        return torch.stack([cx_real - 0.5 * w, cy_real - 0.5 * h, w, h], dim=-1)


def get_tracker_class():
    return STARK_ST
