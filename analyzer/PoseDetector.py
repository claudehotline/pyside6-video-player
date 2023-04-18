import cv2
from mmdeploy_python import Detector, PoseDetector
import numpy as np
from analyzer import device


class PoseDetect():

    def __init__(self, model_path1, model_path2):
        self.detector = Detector(model_path1, device, 0)
        self.pose_detector = PoseDetector(model_path2, device, 0)

    def detect(self, frame):
        # apply detector
        bboxes, labels, _ = self.detector(frame)
        keep = np.logical_and(labels == 0, bboxes[..., 4] > 0.5)
        bboxes = bboxes[keep, :4]
        for bbox in bboxes:
            # print("目标检测框: ",bbox)
            cv2.rectangle(frame, (bbox[0].astype(int), bbox[1].astype(int)), (bbox[2].astype(int), bbox[3].astype(int)), (0, 255, 0), 1)
        result = self.pose_detector(frame, bboxes)

        # print("关键点个数：",result.shape[1])
        keypoint_num = result.shape[1]
        # draw result
        if keypoint_num == 17:
            frame = self.visualize(frame, result, 0.5, 1280)
        elif keypoint_num == 21:
            frame = self.visualize_hand(frame, result, 0.5, 1280)
        elif keypoint_num == 133:
            frame = self.visualize_wholebody(frame, result, 0.5, 1280)

        return frame  
    
    def visualize_hand(self, frame, keypoints, thr=0.5, resize=1280):
        skeleton = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7),
                    (7, 8), (0, 9), (9, 10), (10, 11), (11, 12), (0, 13),
                    (13, 14), (14, 15), (15, 16), (0, 17), (17, 18), (18, 19),
                    (19, 20)]
        palette = [(255, 128, 0), (255, 153, 51), (255, 178, 102), (230, 230, 0),
                (255, 153, 255), (153, 204, 255), (255, 102, 255),
                (255, 51, 255), (102, 178, 255),
                (51, 153, 255), (255, 153, 153), (255, 102, 102), (255, 51, 51),
                (153, 255, 153), (102, 255, 102), (51, 255, 51), (0, 255, 0),
                (0, 0, 255), (255, 0, 0), (255, 255, 255)]
        link_color = [
            0, 0, 0, 0, 7, 7, 7, 7, 9, 9, 9, 9, 16, 16, 16, 16, 16, 16, 16
        ]
        point_color = [16, 16, 16, 16, 16, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0]

        scores = keypoints[..., 2]
        keypoints = keypoints[..., :2].astype(int)

        for kpts, score in zip(keypoints, scores):
            show = [0] * len(kpts)
            for (u, v), color in zip(skeleton, link_color):
                if score[u] > thr and score[v] > thr:
                    cv2.line(frame, kpts[u], tuple(kpts[v]), palette[color], 1,
                            cv2.LINE_AA)
                    show[u] = show[v] = 1
            for kpt, show, color in zip(kpts, show, point_color):
                if show:
                    cv2.circle(frame, kpt, 1, palette[color], 1, cv2.LINE_AA)
        return frame

    def visualize_foot(self, frame, keypoints, thr=0.5, resize=1280):
        skeleton = [(0, 2), (1, 2)]
        palette = [(255, 128, 0), (255, 153, 51)]
        link_color = [0, 1]
        point_color = [0, 1]

        scores = keypoints[..., 2]
        keypoints = keypoints[..., :2].astype(int)
        for kpts, score in zip(keypoints, scores):
            show = [0] * len(kpts)
            for (u, v), color in zip(skeleton, link_color):
                if score[u] > thr and score[v] > thr:
                    cv2.line(frame, kpts[u], tuple(kpts[v]), palette[color], 1,
                            cv2.LINE_AA)
                    show[u] = show[v] = 1
            for kpt, show, color in zip(kpts, show, point_color):
                if show:
                    cv2.circle(frame, kpt, 1, palette[color], 1, cv2.LINE_AA) 
        return frame

    def visualize(self, frame, keypoints, thr=0.5, resize=1280):
        skeleton = [(15, 13), (13, 11), (16, 14), (14, 12), (11, 12), (5, 11),
                    (6, 12), (5, 6), (5, 7), (6, 8), (7, 9), (8, 10), (1, 2),
                    (0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6)]
        palette = [(255, 128, 0), (255, 153, 51), (255, 178, 102), (230, 230, 0),
                (255, 153, 255), (153, 204, 255), (255, 102, 255),
                (255, 51, 255), (102, 178, 255),
                (51, 153, 255), (255, 153, 153), (255, 102, 102), (255, 51, 51),
                (153, 255, 153), (102, 255, 102), (51, 255, 51), (0, 255, 0),
                (0, 0, 255), (255, 0, 0), (255, 255, 255)]
        link_color = [
            0, 0, 0, 0, 7, 7, 7, 9, 9, 9, 9, 9, 16, 16, 16, 16, 16, 16, 16
        ]
        point_color = [16, 16, 16, 16, 16, 9, 9, 9, 9, 9, 9, 0, 0, 0, 0, 0, 0]


        scores = keypoints[..., 2]
        keypoints = keypoints[..., :2].astype(int)

        for kpts, score in zip(keypoints, scores):
            show = [0] * len(kpts)
            for (u, v), color in zip(skeleton, link_color):
                if score[u] > thr and score[v] > thr:
                    cv2.line(frame, kpts[u], tuple(kpts[v]), palette[color], 1,
                            cv2.LINE_AA)
                    show[u] = show[v] = 1
            for kpt, show, color in zip(kpts, show, point_color):
                if show:
                    cv2.circle(frame, kpt, 1, palette[color], 1, cv2.LINE_AA)
        return frame


    def visualize_wholebody(self, frame, keypoints, thr=0.5, resize=1280):
        frame = self.visualize(frame, keypoints=keypoints[:,:17,:], thr=0.5)
        frame = self.visualize_hand(frame, keypoints=keypoints[:,91:112,:], thr=0.5)
        frame = self.visualize_hand(frame, keypoints=keypoints[:,112:133,:], thr=0.5)
        frame = self.visualize_foot(frame, keypoints=keypoints[:,17:20,:], thr=0.5)
        frame = self.visualize_foot(frame, keypoints=keypoints[:,20:23,:], thr=0.5)

        keypoints = keypoints[..., :2].astype(int)

        for kpts in keypoints:
            for kpt in range(len(kpts)):
                if kpt >=23 and kpt <= 90:
                    cv2.circle(frame, kpts[kpt], 1, (255, 255, 255), 1, cv2.LINE_AA)
        
        return frame