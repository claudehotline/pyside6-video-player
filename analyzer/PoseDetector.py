import sys
import os
# sys.path.append('E:/Projects/deeplearning/mmlab/mmdeploy/build/bin/Release')
os.add_dll_directory(
    'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/bin')
os.add_dll_directory(
    'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/lib/x64')
os.add_dll_directory('E:/Projects/deeplearning/mmlab/TensorRT-8.5.3.1/lib')
os.add_dll_directory('H:/opencv/build/x64/vc16/bin')

import cv2
from mmdeploy_python import Detector, PoseDetector
import numpy as np



class PoseDetect():

    def __init__(self, model_path1, model_path2):
        self.detector = Detector(model_path1, 'cuda', 0)
        self.pose_detector = PoseDetector(model_path2, 'cuda', 0)

    def detect(self, frame):
        # apply detector
        bboxes, labels, _ = self.detector(frame)
        keep = np.logical_and(labels == 0, bboxes[..., 4] > 0.6)
        bboxes = bboxes[keep, :4]
        result = self.pose_detector(frame, bboxes)
        # draw result
        frame = self.visualize(frame, result, 0.5, 1280)

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

        scale = resize / max(frame.shape[0], frame.shape[1])

        scores = keypoints[..., 2]
        keypoints = (keypoints[..., :2] * scale).astype(int)

        frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)
        for kpts, score in zip(keypoints, scores):
            show = [0] * len(kpts)
            for (u, v), color in zip(skeleton, link_color):
                if score[u] > thr and score[v] > thr:
                    cv2.line(frame, kpts[u], tuple(kpts[v]), palette[color], 1,
                            cv2.LINE_AA)
                    show[u] = show[v] = 1
            for kpt, show, color in zip(kpts, show, point_color):
                if show:
                    cv2.circle(frame, kpt, 1, palette[color], 2, cv2.LINE_AA)
        return frame