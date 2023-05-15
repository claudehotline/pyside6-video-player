from utils.starktrack.stark_lightning_X_trt import STARK_LightningXtrt_onnx
import cv2

class SotTrackingDetector:

    def __init__(self):
        self.tracker = STARK_LightningXtrt_onnx()

        self.frameCounter = 0
    
    def detect(self, frame):
        bbox = []
        if self.frameCounter == 0:
            bbox = [130, 61, 130 + 65, 61 + 55]
            info = {'init_bbox': bbox}
            self.tracker.initialize(frame, info)
        else:
            print("frameCounter: ", self.frameCounter)
            result = self.tracker.track(frame)
            bbox = result['target_bbox']
            # print(bbox)

        self.frameCounter += 1

        cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 255, 0), 2)
        return frame