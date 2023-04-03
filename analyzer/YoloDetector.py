
import sys
import os
# sys.path.append('E:/Projects/deeplearning/mmlab/mmdeploy/build/bin/Release')
sys.path.append('I:/mmdeploy/build/bin/Release')
# os.add_dll_directory(
#     'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/bin')
# os.add_dll_directory(
#     'C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v11.7/lib/x64')
# os.add_dll_directory('E:/Projects/deeplearning/mmlab/TensorRT-8.5.3.1/lib')
# os.add_dll_directory('H:/opencv/build/x64/vc16/bin')
os.add_dll_directory('D:/opencv/build/x64/vc16/bin')
os.add_dll_directory('D:/onnxruntime-win-x64-1.8.1/lib')

import cv2
from mmdeploy_python import Detector

class YoloDetector():

    def __init__(self, model_path):
        # self.detector = Detector(model_path, 'cuda', 0)
        self.detector = Detector(model_path, 'cpu', 0)

    def detect(self, frame):
        bboxes, labels, _ = self.detector(frame)

        # 使用阈值过滤推理结果，并绘制到原图中
        indices = [i for i in range(len(bboxes))]
        for index, bbox, label_id in zip(indices, bboxes, labels):
            score = bbox[4]
            if score < 0.7:
                continue
            # 绘制bounding box 和 label 文本
            self.draw_labels(frame, bbox, label_id)
        return frame

    def draw_labels(self, frame, bbox, label_id):
        [left, top, right, bottom] = bbox[0:4].astype(int)

        # coco数据集类别标签
        coco_labels = [ 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 
                       'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 
                       'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 
                       'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 
                       'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 
                       'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 
                       'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 
                       'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 
                       'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush' ]
        # coco数据集标签对应的颜色
        coco_colors = [ (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255), (0, 0, 128), (0, 128, 0),
                       (128, 0, 0), (128, 128, 0), (0, 128, 128), (128, 0, 128), (128, 128, 128), (0, 0, 64), (0, 64, 0),
                       (64, 0, 0), (64, 64, 0), (0, 64, 64), (64, 0, 64), (64, 64, 64), (0, 0, 192), (0, 192, 0),
                       (192, 0, 0), (192, 192, 0), (0, 192, 192), (192, 0, 192), (192, 192, 192), (64, 0, 128), (128, 0, 64), (64, 128, 0), (128, 64, 0),
                       (0, 64, 128), (0, 128, 64), (128, 0, 192), (192, 0, 128), (128, 192, 0), (192, 128, 0),
                       (0, 128, 192), (0, 192, 128), (192, 0, 64), (64, 0, 192), (192, 64, 0), (64, 192, 0),
                       (0, 192, 64), (0, 64, 192), (64, 128, 128), (128, 64, 128), (128, 128, 64), (64, 64, 128), (64, 128, 64), (128, 64, 64),
                       (64, 64, 192), (64, 192, 64), (192, 64, 64), (64, 64, 0), (64, 0, 64), (0, 64, 64),
                       (64, 192, 128), (64, 128, 192), (128, 64, 192), (128, 192, 64), (192, 64, 128), (192, 128, 64),
                       (64, 192, 192), (192, 64, 192), (192, 192, 64), (64, 0, 192), (192, 0, 64), (64, 192, 0),
                       (192, 64, 0), (0, 192, 64), (0, 64, 192), (192, 128, 128), (128, 192, 128), (128, 128, 192), (192, 128, 192), (192, 192, 128), (128, 192, 192) ]    
        # 绘制矩形框
        cv2.rectangle(frame, (left, top), (right, bottom), coco_colors[label_id], 1)
        cv2.rectangle(frame, (left, top-20), (left+100, top), coco_colors[label_id], cv2.FILLED)
        # 绘制标签
        cv2.putText(frame, coco_labels[label_id], (left, top-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)