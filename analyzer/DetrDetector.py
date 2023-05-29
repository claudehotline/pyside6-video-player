import cv2
from PIL import Image
from analyzer import device
import numpy as np
import torch
import torchvision.transforms as T
torch.set_grad_enabled(False);

class DetrDetector():

    def __init__(self):
        self.score_threshold = 0.9

        self.model = torch.hub.load('facebookresearch/detr', 'detr_resnet101', pretrained=True)
        self.model.eval();
    
        self.transform = T.Compose([
          T.Resize(800),
          T.ToTensor(),
          T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.coco_labels = [ 'N/A', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
                            'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'N/A',
                            'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse',
                            'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'N/A', 'backpack',
                            'umbrella', 'N/A', 'N/A', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis',
                            'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
                            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'N/A', 'wine glass',
                            'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich',
                            'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
                            'chair', 'couch', 'potted plant', 'bed', 'N/A', 'dining table', 'N/A',
                            'N/A', 'toilet', 'N/A', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
                            'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'N/A',
                            'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
                            'toothbrush' ]
        # coco数据集标签对应的颜色
        self.coco_colors = [ (0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255), (0, 0, 128), (0, 128, 0),
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

    def detect(self, frame):
        img = Image.fromarray(frame)
        img = self.transform(img).unsqueeze(0)
        outputs = self.model(img)

        probas = outputs['pred_logits'].softmax(-1)[0, :, :-1]
        keep = probas.max(-1).values > self.score_threshold
        # convert boxes from [0; 1] to image scales
        bboxes_scaled = self.rescale_bboxes(outputs['pred_boxes'][0, keep], (frame.shape[1], frame.shape[0]))

        img = self.plot_results(frame, probas[keep], bboxes_scaled)
        return img
    
    # for output bounding box post-processing
    def box_cxcywh_to_xyxy(self, x):
        x_c, y_c, w, h = x.unbind(1)
        b = [(x_c - 0.5 * w), (y_c - 0.5 * h),
            (x_c + 0.5 * w), (y_c + 0.5 * h)]
        return torch.stack(b, dim=1)

    def rescale_bboxes(self, out_bbox, size):
        img_w, img_h = size
        b = self.box_cxcywh_to_xyxy(out_bbox)
        b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
        return b
    
    def getbox(self, frame):
        bboxes, labels, _ = self.detector(frame)

        if len(self.detect_labels) != 0:
            keep = np.logical_and(labels == self.detect_labels[0], bboxes[..., 4] > self.score_threshold)
            bboxes = bboxes[keep]
            labels = labels[keep]
        else:
            keep = np.logical_and(bboxes[..., 4] > self.score_threshold)
            bboxes = bboxes[keep]
            labels = labels[keep]
        return bboxes, labels
    
    def plot_results(self, img, prob, boxes):
        for p, (xmin, ymin, xmax, ymax), c in zip(prob, boxes.tolist(), self.coco_colors):
            cl = p.argmax()
            cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), self.coco_colors[cl], 2)
            text = f'{self.coco_labels[cl]}: {p[cl]:0.2f}'
            cv2.putText(img, text, (int(xmin), int(ymin)), cv2.FONT_HERSHEY_SIMPLEX, 1, self.coco_colors[cl], 2)
        return img

    def set_score_threshold(self, threshold):
        self.score_threshold = threshold