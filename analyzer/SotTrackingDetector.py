from utils.starktrack.stark_lightning_X_trt import STARK_LightningXtrt_onnx
from utils.starktrack.stark_s import STARK_S_onnx
from utils.starktrack.stark_st import STARK_ST_onnx
import cv2
import threading

class SotTrackingDetector:

    def __init__(self):
        self.tracker_list = []
        self.tracker_list.append(STARK_ST_onnx(1))
        # self.tracker_list.append(STARK_S_onnx(1))
        # self.tracker_list.append(STARK_LightningXtrt_onnx(1))
        print('init stark_s')
        self.frame_disp = None
        self.is_tracking = False
    
    def detect(self, frame):
        if self.is_tracking == True:
            self.frame_disp = frame.copy()
            for tracker in self.tracker_list:
                if tracker.frame_id == 0:
                    thread = threading.Thread(target=self.init_frame_detect, args=(tracker, frame,))
                    thread.start()
                    thread.join()
                else:
                    result = tracker.track(frame)
                    bbox = result['target_bbox']
                    if len(bbox) == 4:
                    # 在frame_disp上画出bbox
                        cv2.rectangle(self.frame_disp, (int(bbox[0]), int(bbox[1])), (int(bbox[0])+int(bbox[2]), int(bbox[1])+ int(bbox[3])), (0, 255, 0), 2)
                    # 在frame_disp上画出 self.centerpoints的所有点
                    for i in range(len(tracker.center_pos)):
                        cv2.circle(self.frame_disp, (int(tracker.center_pos[i][0]), int(tracker.center_pos[i][1])), 2, (0, 0, 255), 2)
            if self.frame_disp is not None:
                return self.frame_disp
            else: return frame
        else:
            return frame
    
    def init_frame_detect(self, tracker, frame):
        self.frame_disp = frame.copy()
        cv2.namedWindow("选择跟踪目标", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("选择跟踪目标", 800, 600)
        x, y, w, h = cv2.selectROI('选择跟踪目标', self.frame_disp, fromCenter=False)
        bbox = [x, y, w, h]
        info = {'init_bbox': bbox}
        tracker.initialize(frame, info)
        cv2.rectangle(self.frame_disp, (int(bbox[0]), int(bbox[1])), (int(bbox[0]) + int(bbox[2]), int(bbox[1]) + int(bbox[3])), (0, 255, 0), 2)
        # 在frame_disp上画出中点
        cv2.circle(self.frame_disp, (int(int(bbox[0]) + int(bbox[2]) / 2), int(int(bbox[1]) + int(bbox[3]) / 2)), 2, (0, 0, 255), 2)
        cv2.destroyAllWindows()

    def add_tracker(self):
        self.tracker_list.append(STARK_LightningXtrt_onnx(len(self.tracker_list)+1))

    def start_tracking(self):
        self.is_tracking = True

    def stop_tracking(self):
        self.is_tracking = False
        self.frame_disp = None
        self.tracker_list = []