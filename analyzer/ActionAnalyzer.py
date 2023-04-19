import cv2
import copy as cp
import torch
from analyzer import device
import numpy as np
import mmengine
from mmengine.runner import load_checkpoint
from mmengine.structures import InstanceData
import mmcv
from mmaction.apis import (detection_inference, inference_recognizer,
                        init_recognizer, pose_inference)
from mmaction.registry import VISUALIZERS, MODELS
from mmengine.utils import track_iter_progress
from mmaction.structures import ActionDataSample

try:
    import moviepy.editor as mpy
except ImportError:
    raise ImportError('Please install moviepy to enable output file')


# FONTFACE = cv2.FONT_HERSHEY_DUPLEX
# FONTSCALE = 0.75
# FONTCOLOR = (255, 255, 255)  # BGR, white
# THICKNESS = 1
# LINETYPE = 1

FONTFACE = cv2.FONT_HERSHEY_DUPLEX
FONTSCALE = 0.5
FONTCOLOR = (255, 255, 255)  # BGR, white
MSGCOLOR = (128, 128, 128)  # BGR, gray
THICKNESS = 1
LINETYPE = 1

def hex2color(h):
    """Convert the 6-digit hex string to tuple of 3 int value (RGB)"""
    return (int(h[:2], 16), int(h[2:4], 16), int(h[4:], 16))


plate_blue = '03045e-023e8a-0077b6-0096c7-00b4d8-48cae4'
plate_blue = plate_blue.split('-')
plate_blue = [hex2color(h) for h in plate_blue]
plate_green = '004b23-006400-007200-008000-38b000-70e000'
plate_green = plate_green.split('-')
plate_green = [hex2color(h) for h in plate_green]

class ActionAnalyzer:

    def __init__(self, model_path):

        self.clip = []

        self.det_config = 'D:/Projects/deeplearning/mmlab/mmaction2/demo/demo_configs/faster-rcnn_r50_fpn_2x_coco_infer.py'
        self.det_checkpoint = 'D:/Projects/deeplearning/mmlab/mmaction2/faster_rcnn_r50_fpn_2x_coco_bbox_mAP-0.384_20200504_210434-a5d8aa15.pth'

        # self.pose_config = 'D:/Projects/deeplearning/mmlab/mmaction2/demo/demo_configs/td-hm_hrnet-w32_8xb64-210e_coco-256x192_infer.py'
        # self.pose_checkpoint = 'D:/Projects/deeplearning/mmlab/mmaction2/hrnet_w32_coco_256x192-c78dce93_20200708.pth'
        
        self.config = 'D:/Projects/deeplearning/mmlab/mmaction2/configs/detection/slowfast/slowfast_kinetics400-pretrained-r50_8xb6-8x8x1-cosine-10e_ava22-rgb.py'
        # self.checkpoint = 'D:/Projects/deeplearning/mmlab/mmaction2/slowfast_kinetics400-pretrained-r50_8xb16-4x16x1-20e_ava21-rgb_20220906-5180ea3c.pth'
        self.checkpoint = 'D:/Projects/deeplearning/mmlab/mmaction2/slowfast_kinetics400-pretrained-r50_8xb6-8x8x1-cosine-10e_ava22-rgb_20220906-d934a48f.pth'
        self.config = mmengine.Config.fromfile(self.config)

        self.label_map = self.load_label_map('annotations/label_map.txt')

        self.vis_frames = []

        self.results = []

    # def detect(self, frame):
    #     self.clip.append(frame)
    #     if len(self.clip) == 8:
    #     # frame = [frame]
    #         det_results, _ = detection_inference(self.det_config, self.det_checkpoint,
    #                                             self.clip, device=device)
    #         torch.cuda.empty_cache()
    #         pose_results, pose_data_samples = pose_inference(self.pose_config,
    #                                                         self.pose_checkpoint,
    #                                                         self.clip, det_results,
    #                                                         device)
    #         torch.cuda.empty_cache()

    #         fake_anno = dict(
    #             frame_dir=self.clip,
    #             label=-1,
    #             img_shape=self.clip[0].shape[:2],
    #             original_shape=self.clip[0].shape[:2],
    #             start_index=0,
    #             modality='Pose',
    #             total_frames=len(self.clip)
    #         )

    #         num_person = max([len(x['keypoints']) for x in pose_results])

    #         num_keypoint = 17
    #         keypoint = np.zeros((len(self.clip), num_person, num_keypoint, 2),
    #                             dtype=np.float16)
    #         keypoint_score = np.zeros((len(self.clip), num_person, num_keypoint),
    #                                 dtype=np.float16)
    #         for i, poses in enumerate(pose_results):
    #             for j in range(len(poses['keypoints'])):
    #                 keypoint[i][j] = poses['keypoints'][j]
    #                 keypoint_score[i][j] = poses['keypoint_scores'][j]
    #             # keypoint_score[i] = poses['keypoint_scores']

    #         fake_anno['keypoint'] = keypoint.transpose((1, 0, 2, 3))
    #         fake_anno['keypoint_score'] = keypoint_score.transpose((1, 0, 2))

    #         config = mmengine.Config.fromfile(self.config)
    #         # config.merge_from_dict(args.cfg_options)

    #         model = init_recognizer(config, self.checkpoint, device)
    #         # print('fake_anno: ', fake_anno['img_shape'])
    #         result = inference_recognizer(model, fake_anno)

    #         max_pred_index = result.pred_scores.item.argmax().item()
    #         # with open(self.label_map) as f:
    #         #     label_map = [x.strip() for x in f.readlines()]
    #         # label_map = [x.strip() for x in open(self.label_map).readlines()]
    #         action_label = self.label_map[max_pred_index]
    #         print(action_label)
    #         self.visualize(self.clip, pose_data_samples, action_label)
    #         self.clip = []
    #     return np.array(frame)
    
    def detect(self, frame):
        self.clip.append(frame)
        if len(self.clip) == 8:

            h, w, _ = self.clip[0].shape

            # resize frames to shortside
            new_w, new_h = mmcv.rescale_size((w, h), (256, np.Inf))
            frames = [mmcv.imresize(img, (new_w, new_h)) for img in self.clip]
            w_ratio, h_ratio = new_w / w, new_h / h

            human_detections, _ = detection_inference(self.det_config,
                                            self.det_checkpoint,
                                            self.clip,
                                            0.5,
                                            0, device)
            # print(human_detections[0])
            if(len(human_detections[0]) > 0):
            
                torch.cuda.empty_cache()

                for i in range(len(human_detections)):
                    det = human_detections[i]
                    det[:, 0:4:2] *= w_ratio
                    det[:, 1:4:2] *= h_ratio
                    human_detections[i] = torch.from_numpy(det[:, :4]).to(device)
            
                try:
                    self.config['model']['test_cfg']['rcnn'] = dict(action_thr=0)
                except KeyError:
                    pass

                self.config.model.backbone.pretrained = None
                model = MODELS.build(self.config.model)

                load_checkpoint(model, self.checkpoint, map_location=device)
                model.to(device)
                model.eval()

                predictions = []
                img_norm_cfg = dict(
                    mean=np.array(self.config.model.data_preprocessor.mean),
                    std=np.array(self.config.model.data_preprocessor.std),
                    to_rgb=False
                )

                # Normalize
                imgs = [ x.astype(np.float32) for x in frames]
                _ = [mmcv.imnormalize(x, **img_norm_cfg) for x in imgs]
                
                # THWC -> CTHW -> 1CTHW
                input_array = np.stack(imgs).transpose((3,0,1,2))[np.newaxis]
                input_tensor = torch.from_numpy(input_array).to(device)

                datasample = ActionDataSample()
                datasample.proposals = InstanceData(bboxes=human_detections[7])
                datasample.set_metainfo(dict(img_shape=(new_h, new_w)))

                with torch.no_grad():
                    result = model(input_tensor, [datasample], mode='predict')
                    scores = result[0].pred_instances.scores
                    prediction = []

                    # N proposals
                    for i in range(human_detections[7].shape[0]):
                        prediction.append([])
                    # Perform action score thr
                    print('scores.shape = ', scores.shape)
                    for i in range(scores.shape[1]):
                        if i not in self.label_map:
                            continue
                        for j in range(human_detections[7].shape[0]):
                            if scores[j, i] > 0.5:
                                prediction[j].append((self.label_map[i], scores[j,i].item()))
                    predictions.append(prediction)

                self.results = []
                for human_detection, prediction in zip(human_detections, predictions):
                    self.results.append(self.pack_result(human_detection, prediction, new_h, new_w))
                self.vis_frames = self.visualize(self.clip, self.results)
                for i in range(len(self.vis_frames)):
                    cv2.imwrite('vis_frame_{}.jpg'.format(i), self.vis_frames[i])
                print(predictions)

            self.clip = []

        if len(self.results) > 0:
            frame = frame[np.newaxis, ...]
            frame = self.visualize(frame, [self.results[-1]])[0]
            # print('frame.shape = ', frame.shape)
        return frame

    # def visualize(self, frames, data_samples, action_label):
    #   pose_config = mmengine.Config.fromfile(self.pose_config)
    #   visualizer = VISUALIZERS.build(pose_config.visualizer)
    #   visualizer.set_dataset_meta(data_samples[0].dataset_meta)

    #   vis_frames = []
    #   print('Drawing skeleton for each frame')
    #   for d, f in track_iter_progress(list(zip(data_samples, frames))):
    #     #   f = mmcv.imconvert(f, 'bgr', 'rgb')
    #       visualizer.add_datasample(
    #           'result',
    #           f,
    #           data_sample=d,
    #           draw_gt=False,
    #           draw_heatmap=False,
    #           draw_bbox=True,
    #           show=False,
    #           wait_time=0,
    #           out_file=None,
    #           kpt_thr=0.3)
    #       vis_frame = visualizer.get_image()
    #       cv2.putText(vis_frame, action_label, (10, 30), FONTFACE, FONTSCALE,
    #                   FONTCOLOR, THICKNESS, LINETYPE)
    #       vis_frames.append(vis_frame)
    #   print('vis_frame length = ', len(vis_frames))
    #   for i in range(len(vis_frames)):
    #       print(i)
    #       cv2.imwrite('result{}.jpg'.format(i), vis_frames[i])

    #   vid = mpy.ImageSequenceClip(vis_frames, fps=24)
    #   vid.write_videofile('result.mp4', remove_temp=True)    

    def pack_result(self, human_detection, result, img_h, img_w):
        """Short summary.

        Args:
            human_detection (np.ndarray): Human detection result.
            result (type): The predicted label of each human proposal.
            img_h (int): The image height.
            img_w (int): The image width.
        Returns:
            tuple: Tuple of human proposal, label name and label score.
        """
        human_detection[:, 0::2] /= img_w
        human_detection[:, 1::2] /= img_h
        results = []
        if result is None:
            return None
        for prop, res in zip(human_detection, result):
            res.sort(key=lambda x: -x[1])
            results.append(
                (prop.data.cpu().numpy(), [x[0] for x in res], [x[1]
                                                                for x in res]))
        return results

    def abbrev(self, name):
        """Get the abbreviation of label name:

        'take (an object) from (a person)' -> 'take ... from ...'
        """
        while name.find('(') != -1:
            st, ed = name.find('('), name.find(')')
            name = name[:st] + '...' + name[ed + 1:]
        return name

    def visualize(self, frames, annotations, plate=plate_blue, max_num=5):
        """Visualize frames with predicted annotations.

        Args:
            frames (list[np.ndarray]): Frames for visualization, note that
                len(frames) % len(annotations) should be 0.
            annotations (list[list[tuple]]): The predicted results.
            plate (str): The plate used for visualization. Default: plate_blue.
            max_num (int): Max number of labels to visualize for a person box.
                Default: 5.
        Returns:
            list[np.ndarray]: Visualized frames.
        """

        assert max_num + 1 <= len(plate)
        plate = [x[::-1] for x in plate]
        frames_out = cp.deepcopy(frames)
        nf, na = len(frames), len(annotations)
        assert nf % na == 0
        nfpa = len(frames) // len(annotations)
        anno = None
        h, w, _ = frames[0].shape
        scale_ratio = np.array([w, h, w, h])
        for i in range(na):
            anno = annotations[i]
            if anno is None:
                continue
            for j in range(nfpa):
                ind = i * nfpa + j
                frame = frames_out[ind]
                for ann in anno:
                    box = ann[0]
                    label = ann[1]
                    if not len(label):
                        continue
                    score = ann[2]
                    # print("box = ", box)
                    box = (box * scale_ratio).astype(np.int64)
                    # print("box_scale = ", box)
                    st, ed = tuple(box[:2]), tuple(box[2:])
                    cv2.rectangle(frame, st, ed, plate[0], 2)
                    for k, lb in enumerate(label):
                        if k >= max_num:
                            break
                        text = self.abbrev(lb)
                        text = ': '.join([text, str(score[k])])
                        location = (0 + st[0], 18 + k * 18 + st[1])
                        textsize = cv2.getTextSize(text, FONTFACE, FONTSCALE,
                                                THICKNESS)[0]
                        textwidth = textsize[0]
                        diag0 = (location[0] + textwidth, location[1] - 14)
                        diag1 = (location[0], location[1] + 2)
                        cv2.rectangle(frame, diag0, diag1, plate[k + 1], -1)
                        cv2.putText(frame, text, location, FONTFACE, FONTSCALE,
                                    FONTCOLOR, THICKNESS, LINETYPE)

        return frames_out

    def load_label_map(self, file_path):
        """Load Label Map.

        Args:
            file_path (str): The file path of label map.
        Returns:
            dict: The label map (int -> label name).
        """
        lines = open(file_path).readlines()
        lines = [x.strip().split(': ') for x in lines]
        return {int(x[0]): x[1] for x in lines}
