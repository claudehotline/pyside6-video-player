import sys
import os
sys.path.append('I:/mmdeploy/build/bin/Release')
os.add_dll_directory('D:/onnxruntime-win-x64-1.8.1/lib')
os.add_dll_directory('D:/opencv/build/x64/vc16/bin')


import cv2
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from mmdeploy_python import Detector, Segmentor, PoseDetector, VideoRecognizer
from main import Ui_MainWindow
import numpy as np

class VideoPlayer(QObject):

    def __init__(self, video_path):
        QObject.__init__(self)
        # 创建 VideoCapture 对象并指定要读取的视频文件路径
        self.cap = cv2.VideoCapture(video_path)

        # 获取视频的帧率、宽度和高度
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def set_detector(self, detector):
        self.detector = detector

    def playVideo(self):
        while True:
            ret, frame = self.cap.read()

            if not ret:
              break
            self.detector.detect(frame)


class YoloDetect(QObject):
    
    image = Signal(np.ndarray)
    result = Signal(np.ndarray)
    finished = Signal()

    def __init__(self, model):
        QObject.__init__(self)
        # 创建 VideoCapture 对象并指定要读取的视频文件路径
        self.cap = cv2.VideoCapture('04.mp4')

        # 获取视频的帧率、宽度和高度
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.detector = Detector('model/'+model, 'cpu', 0)


    def detect(self):
        while True:
            ret, frame = self.cap.read()

            if not ret:
              break
            frame_org = frame
            frame = cv2.resize(frame, (int(852), int(480)))
            bboxes, labels, _ = self.detector(frame)

            # 使用阈值过滤推理结果，并绘制到原图中
            indices = [i for i in range(len(bboxes))]
            for index, bbox, label_id in zip(indices, bboxes, labels):
                # [left, top, right, bottom], score = bbox[0:4].astype(int),  bbox[4]
                score = bbox[4]
                if score < 0.7:
                    continue
                # 绘制bounding box 和 label 文本    
                self.draw_labels(frame, bbox, label_id)
                # cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0))

            self.image.emit(frame_org)
            self.result.emit(frame)
        self.finished.emit()

    def draw_labels(self, frame, bbox, label_id):
        [left, top, right, bottom] = bbox[0:4].astype(int)

        # 绘制矩形框
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # 绘制标签
        cv2.putText(frame, str(label_id), (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

class SegmentDetect(QObject):
    
    image = Signal(np.ndarray)
    result = Signal(np.ndarray)
    finished = Signal()

    def __init__(self, model):
        QObject.__init__(self)
        # 创建 VideoCapture 对象并指定要读取的视频文件路径
        self.cap = cv2.VideoCapture('04.mp4')

        # 获取视频的帧率、宽度和高度
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # self.detector = Detector('model/'+model, 'cpu', 0)
        self.seg_detector = Segmentor('model/'+model, 'cpu', 0)
        # self.pose_detector = PoseDetector(model_path='model/pose', device_name='cpu', device_id=0)
        # self.action_detector = VideoRecognizer(model_path='model/action', device_name='cpu', device_id=0)
    
    def detect(self):
        while True:
            ret, frame = self.cap.read()

            if not ret:
                break
            frame_org = frame
            seg = self.seg_detector(frame)

            if seg.dtype == np.float32:
                seg = np.argmax(seg, axis=0)

            palette = self.get_palette()

            color_seg = np.zeros((seg.shape[0], seg.shape[1], 3), dtype=np.uint8)
            for label, color in enumerate(palette):
                color_seg[seg == label, :] = color
            # convert to BGR
            color_seg = color_seg[..., ::-1]

            frame = frame * 0.5 + color_seg * 0.5
            frame = frame.astype(np.uint8)

            self.image.emit(frame_org)
            self.result.emit(frame)
    
    def get_palette(self, num_classes=256):
        state = np.random.get_state()
        # random color
        np.random.seed(42)
        palette = np.random.randint(0, 256, size=(num_classes, 3))
        np.random.set_state(state)
        return [tuple(c) for c in palette]
    

class PoseDetect(QObject):
    
    image = Signal(np.ndarray)
    result = Signal(np.ndarray)
    finished = Signal()

    def __init__(self, model):
        QObject.__init__(self)
        # 创建 VideoCapture 对象并指定要读取的视频文件路径
        self.cap = cv2.VideoCapture('04.mp4')

        # 获取视频的帧率、宽度和高度
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.detector = Detector('model/yolov8', 'cpu', 0)
        # self.seg_detector = Segmentor('model/'+model, 'cpu', 0)
        self.pose_detector = PoseDetector('model/pose', 'cpu', 0)

    def detect(self):
        while True:
            ret, frame = self.cap.read()

            if not ret:
              break
            frame_org = frame.copy()
     
            # apply detector
            bboxes, labels, _ = self.detector(frame)
            keep = np.logical_and(labels == 0, bboxes[..., 4] > 0.6)
            bboxes = bboxes[keep, :4]
            result = self.pose_detector(frame, bboxes)
            # draw result
            frame = self.visualize(frame, result, 0.5, 1280)
            
            self.image.emit(frame_org)
            self.result.emit(frame)

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


class MainWindow(QMainWindow):
    
    begin = Signal()
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # self.label_1 = QLabel(self)
        # self.label_1.setMinimumSize(int(852/1.5), int(480/1.5))

        # self.label_2 = QLabel(self)
        # self.label_2.setMinimumSize(int(852/1.5), int(480/1.5))

        # # label_1 和 label_2 水平布局
        # layout = QHBoxLayout()
        # layout.addWidget(self.label_1)
        # layout.addWidget(self.label_2)
        # widget = QWidget()
        # widget.setLayout(layout)
        # self.setCentralWidget(widget)

        

        self.label_1 = self.ui.label_1
        self.label_2 = self.ui.label_2
        self.model_selector = self.ui.model
        # 读取model目录项的目录名
        self.model_dir = os.listdir('model')
        print(self.model_dir)
        # 设置model_selector的选项
        self.model_selector.addItems(self.model_dir)
        self.model_selector.setCurrentIndex(0)
        self.model_selector.currentTextChanged.connect(self.text_changed)

        # self.begin.emit()

    def text_changed(self):
        model = self.model_selector.currentText()

        if model == 'yolov8':
            self.detector = YoloDetect(model)
        elif model == 'seg':
            self.detector = SegmentDetect(model)
        elif model == 'pose':
            self.detector = PoseDetect(model)
    
        self.detector_thread = QThread()
        self.detector.image.connect(lambda x: self.show_image(x, self.label_1))
        self.detector.result.connect(lambda x: self.show_image(x, self.label_2))

        self.begin.connect(self.detector.detect)
        # self.begin.connect(self.detector.seg_detect)
        # self.begin.connect(self.detector.pose_detect)
        # self.begin.connect(self.detector.action_detect)

        self.detector.moveToThread(self.detector_thread)
        self.detector.finished.connect(self.detector.deleteLater)
        self.detector.finished.connect(self.detector_thread.deleteLater)
        self.detector_thread.start()
        self.begin.emit()

    def closeEvent(self, event):
        if self.detector_thread.isRunning:
            self.detector_thread.terminate()
            self.detector_thread.wait()
            self.detector.cap.release()
        event.accept()

    @staticmethod
    def show_image(img_src, label):
        image = QImage(img_src, img_src.shape[1], img_src.shape[0], QImage.Format_BGR888)
        image = image.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(QPixmap.fromImage(image))

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())