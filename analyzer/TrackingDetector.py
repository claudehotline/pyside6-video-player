import numpy as np
import torch
from analyzer.YoloDetector import YoloDetector
from utils.deep_sort import DeepSort
from utils.bytetrack.byte_tracker import BYTETracker
import cv2

class TrackingDetector:

    def __init__(self, model_path1, model_path2, tracking_class=[]):
        # super(TrackingDetecor, self).__init__()
        self.model = YoloDetector(model_path1, tracking_class)

        self.deepsort = DeepSort(model_path2,
                    max_dist=0.2, min_confidence=0.3,
                    nms_max_overlap=0.5, max_iou_distance=0.7,
                    max_age=70, n_init=3, nn_budget=100,
                    use_cuda=True)
        
        self.tracker = BYTETracker(det_thresh=0.6, 
                    track_thresh=0.2, track_buffer=70, 
                    match_thresh=0.9, frame_rate=30)

        self.frameCounter = 0
    
    def detect(self, frame):
        self.frameCounter += 1
        # bboxes, _ = self.model.getbox(frame)
        
        # for t in output_stracks:
        #     bbox = t.tlwh
        #     x1, y1, w, h = [int(i) for i in bbox]
        #     x2, y2 = x1 + w, y1 + h
        #     tid = t.track_id
        #     cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
        #     cv2.putText(frame, str(tid), (int(x1), int(y1)), 0, 5e-3 * 200, (0,255,0),2)
        bboxes2draw = self.update_tracker(frame)
        self.drawbox(frame, bboxes2draw)
        return frame
    
    def update_tracker(self, image):
        bboxes, labels = self.model.getbox(image)
        # print('bboxes shape: ', bboxes.shape)
        # print('bboxes: ', bboxes)
        # num_box = len(bboxes)

        # pred_boxes = np.zeros((num_box, 6))
        # pred_boxes[:, 0:4] = bboxes[:, :4]
        # pred_boxes[:, 4] = labels
        # pred_boxes[:, 5] = bboxes[:, 4]

        # bbox_xywh = []
        # confs = []
        # bboxes2draw = []
        # if len(pred_boxes):
        #     # Adapt detections to deep sort input format
        #     for x1, y1, x2, y2, _, conf in pred_boxes:
        #         obj = [
        #             int((x1+x2)/2), int((y1+y2)/2),
        #             x2-x1, y2-y1
        #         ]
        #         bbox_xywh.append(obj)
        #         confs.append(conf)

        #     xywhs = torch.Tensor(bbox_xywh)
        #     confss = torch.Tensor(confs)

        #     # Pass detections to deepsort
        #     outputs = self.deepsort.update(xywhs, confss, image)

        #     for value in list(outputs):
        #         x1,y1,x2,y2,track_id = value
        #         bboxes2draw.append(
        #             (x1, y1, x2, y2, '', track_id)
        #         )

        bboxes2draw = self.tracker.update(bboxes, (image.shape[1], image.shape[0]), (image.shape[1], image.shape[0]))
        # print("bboxes2draw: ",bboxes2draw)
        bboxes2draw = np.array([[int(box.tlbr[0]), int(box.tlbr[1]), int(box.tlbr[2]), int(box.tlbr[3]), 2, int(box.track_id)]  for box in bboxes2draw])

        # print('bboxes2draw shape: ', bboxes2draw.shape)
        # print('bboxes2draw: ', bboxes2draw)
        return bboxes2draw
    
    def drawbox(self, image, bboxes, line_thickness=None):
        tl = line_thickness or round(
            0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
        for (x1, y1, x2, y2, cls_id, track_id) in bboxes:
            c1, c2 = (x1, y1), (x2, y2)
            color = (0, 255, 0)
            cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
            tf = max(tl - 1, 1)  # font thickness
            t_size = cv2.getTextSize(cls_id, 0, fontScale=tl / 3, thickness=tf)[0]
            c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
            cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
            cv2.putText(image, '{} ID-{}'.format(cls_id, track_id), (c1[0], c1[1] - 2), 0, tl / 3,
                        [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)