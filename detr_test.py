import cv2
from PIL import Image
from analyzer import device
import numpy as np
import torch
import torchvision.transforms as T
torch.set_grad_enabled(False);

coco_labels = [ 'N/A', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
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

coco_colors = [ [0.000, 0.447, 0.741], [0.850, 0.325, 0.098], [0.929, 0.694, 0.125],
          [0.494, 0.184, 0.556], [0.466, 0.674, 0.188], [0.301, 0.745, 0.933] ]

# for output bounding box post-processing
def box_cxcywh_to_xyxy(x):
    x_c, y_c, w, h = x.unbind(1)
    b = [(x_c - 0.5 * w), (y_c - 0.5 * h),
        (x_c + 0.5 * w), (y_c + 0.5 * h)]
    return torch.stack(b, dim=1)

def rescale_bboxes(out_bbox, size):
    img_w, img_h = size
    b = box_cxcywh_to_xyxy(out_bbox)
    b = b * torch.tensor([img_w, img_h, img_w, img_h], dtype=torch.float32)
    return b

def plot_results(img, prob, boxes):
    for p, (xmin, ymin, xmax, ymax), c in zip(prob, boxes.tolist(), coco_colors):
        cv2.rectangle(img, (int(xmin), int(ymin)), (int(xmax), int(ymax)), c, 2)
        cl = p.argmax()
        text = f'{coco_labels[cl]}: {p[cl]:0.2f}'
        cv2.putText(img, text, (int(xmin), int(ymin)), cv2.FONT_HERSHEY_SIMPLEX, 1, c, 2)
    return img


if __name__ == '__main__':
    
    score_threshold = 0.5

    model = torch.hub.load('facebookresearch/detr', 'detr_resnet50', pretrained=True)
    model.eval();

    transform = T.Compose([
      T.Resize(800),
      T.ToTensor(),
      T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    cap = cv2.VideoCapture('video/03.mp4')
    # 获取帧率
    fps = cap.get(cv2.CAP_PROP_FPS)

    while True:
        ret, frame = cap.read()
        img = Image.fromarray(frame)

        img = transform(img).unsqueeze(0)
        outputs = model(img)

        probas = outputs['pred_logits'].softmax(-1)[0, :, :-1]
        keep = probas.max(-1).values > score_threshold
        # convert boxes from [0; 1] to image scales
        bboxes_scaled = rescale_bboxes(outputs['pred_boxes'][0, keep], (frame.shape[1], frame.shape[0]))
        
        img = plot_results(frame, probas[keep], bboxes_scaled)

        cv2.namedWindow('frame', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('frame', 800, 600)
        cv2.imshow('frame', img)

        if cv2.waitKey(int(1000/fps)) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()