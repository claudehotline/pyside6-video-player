from utils.starktrack.stark_lightning_X_trt import STARK_LightningXtrt_onnx
import cv2
import threading

class SotTrackingDetector:

    def __init__(self):
        self.tracker = STARK_LightningXtrt_onnx()
        self.centerpoints = []
        self.frameCounter = 0
        self.frame_disp = None
        self.is_tracking = True
    
    def detect(self, frame):
        if self.is_tracking == True:
            if self.frameCounter == 0:
                thread = threading.Thread(target=self.init_frame_detect, args=(frame,))
                thread.start()
                thread.join()
            else:
                self.frame_disp = frame.copy()
                result = self.tracker.track(frame)
                bbox = result['target_bbox']
                cv2.rectangle(self.frame_disp, (int(bbox[0]), int(bbox[1])), (int(bbox[0])+int(bbox[2]), int(bbox[1])+ int(bbox[3])), (0, 255, 0), 2)
                # 在frame_disp上画出 self.centerpoints的所有点
                self.centerpoints.append([int(bbox[0]) + int(bbox[2]) / 2, int(bbox[1]) + int(bbox[3]) / 2])
                for i in range(len(self.centerpoints)):
                    cv2.circle(self.frame_disp, (int(self.centerpoints[i][0]), int(self.centerpoints[i][1])), 2, (0, 0, 255), 2)

            self.frameCounter += 1
            return self.frame_disp
        else:
            self.frameCounter = 0
            return frame
    
    def init_frame_detect(self, frame):
        self.frame_disp = frame.copy()
        cv2.namedWindow("选择跟踪目标", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("选择跟踪目标", 800, 600)
        x, y, w, h = cv2.selectROI('选择跟踪目标', self.frame_disp, fromCenter=False)
        bbox = [x, y, w, h]
        info = {'init_bbox': bbox}
        self.centerpoints.append([int(bbox[0]) + int(bbox[2]) / 2, int(bbox[1]) + int(bbox[3]) / 2])
        self.tracker.initialize(frame, info)
        cv2.rectangle(self.frame_disp, (int(bbox[0]), int(bbox[1])), (int(bbox[0]) + int(bbox[2]), int(bbox[1]) + int(bbox[3])), (0, 255, 0), 2)
        # 在frame_disp上画出中点
        cv2.circle(self.frame_disp, (int(int(bbox[0]) + int(bbox[2]) / 2), int(int(bbox[1]) + int(bbox[3]) / 2)), 2, (0, 0, 255), 2)
        cv2.destroyAllWindows()

    def start_tracking(self):
        self.is_tracking = True

    def stop_tracking(self):
        self.is_tracking = False
        self.frameCounter = 0
        self.centerpoints = []
        self.frame_disp = None
        self.tracker = STARK_LightningXtrt_onnx()