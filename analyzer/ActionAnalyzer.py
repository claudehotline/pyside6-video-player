import cv2
import torch
from analyzer import device
import numpy as np
import mmengine
import mmcv
from mmaction.apis import (detection_inference, inference_recognizer,
                          init_recognizer, pose_inference)
from mmaction.registry import VISUALIZERS

class ActionAnalyzer:

    def __init__(self, model_path):

        self.clip = []

        self.det_config = ''
        self.det_checkpoint = ''

        self.pose_config = ''
        self.pose_checkpoint = ''
        
        self.config = ''
        self.checkpoint = ''

        self.label_map = 'annotations/label_map_ntu60.txt'

    def detect(self, clip):
        det_results, _ = detection_inference(self.det_config, self.det_checkpoint,
                                             clip, device=device)
        torch.cuda.empty_cache()
        pose_results, pose_data_samples = pose_inference(self.pose_config,
                                                         self.pose_checkpoint,
                                                         clip, det_results,
                                                         device)
        torch.cuda.empty_cache()

        fake_anno = dict(
          frame_dir='',
          label=-1,
          img_shape=clip[0].shape,
          original_shape=clip[0].shape,
          start_index=0,
          modality='Pose',
          total_frames=len(self.clip))
        num_person = max([len(x['keypoints']) for x in pose_results])

        num_keypoint = 17
        keypoint = np.zeros((len(self.clip), num_person, num_keypoint, 2),
                            dtype=np.float16)
        keypoint_score = np.zeros((len(self.clip), num_person, num_keypoint),
                                  dtype=np.float16)
        for i, poses in enumerate(pose_results):
            keypoint[i] = poses['keypoints']
            keypoint_score[i] = poses['keypoint_scores']

        fake_anno['keypoint'] = keypoint.transpose((1, 0, 2, 3))
        fake_anno['keypoint_score'] = keypoint_score.transpose((1, 0, 2))

        config = mmengine.Config.fromfile(self.config)
        # config.merge_from_dict(args.cfg_options)

        model = init_recognizer(config, self.checkpoint, device)
        result = inference_recognizer(model, fake_anno)

        max_pred_index = result.pred_scores.item.argmax().item()
        label_map = [x.strip() for x in open(self.label_map).readlines()]
        action_label = label_map[max_pred_index]

        self.visualize(args, frames, pose_data_samples, action_label)

    def visualize(self, args, frames, data_samples, action_label):
      pose_config = mmengine.Config.fromfile(self.pose_config)
      visualizer = VISUALIZERS.build(pose_config.visualizer)
      visualizer.set_dataset_meta(data_samples[0].dataset_meta)

      vis_frames = []
      print('Drawing skeleton for each frame')
      for d, f in track_iter_progress(list(zip(data_samples, frames))):
          f = mmcv.imconvert(f, 'bgr', 'rgb')
          visualizer.add_datasample(
              'result',
              f,
              data_sample=d,
              draw_gt=False,
              draw_heatmap=False,
              draw_bbox=True,
              show=False,
              wait_time=0,
              out_file=None,
              kpt_thr=0.3)
          vis_frame = visualizer.get_image()
          cv2.putText(vis_frame, action_label, (10, 30), FONTFACE, FONTSCALE,
                      FONTCOLOR, THICKNESS, LINETYPE)
          vis_frames.append(vis_frame)

      vid = mpy.ImageSequenceClip(vis_frames, fps=24)
      vid.write_videofile(args.out_filename, remove_temp=True)    

