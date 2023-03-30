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
import time

class VideoPlayer(QObject):

    finished = Signal()
    progress_slider = Signal(int)
    image = Signal(np.ndarray)
    result = Signal(np.ndarray)

    def __init__(self, video_path):
        QObject.__init__(self)
        # 创建 VideoCapture 对象并指定要读取的视频文件路径
        self.cap = cv2.VideoCapture(video_path)

        # 获取视频的帧率、宽度和高度
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # 获取self.cap的总帧数
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        self.play = False


    # def set_video_path(self, video_path):
    #     self.cap = cv2.VideoCapture(video_path)

    def set_detector(self, detector):
        self.detector = detector

    def set_frame(self, frame):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, int(self.total_frames * frame / 100))

    def set_play_status(self, status):
        self.play = status

    def get_play_status(self):
        return self.play

    def playVideo(self):
        start_time = time.time()
        count = 0
        fps = 0
        while self.play:
            ret, frame = self.cap.read()

            frame_copy = frame.copy()

            pos = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            self.progress_slider.emit(int(pos/self.total_frames*100))

            if not ret:
              break

            result = self.detector.detect(frame)

            count += 1
            end_time = time.time()
            if end_time - start_time >= 1:
                fps = count
                count = 0
                start_time = time.time()

            cv2.putText(result, 'FPS: {}'.format(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            self.image.emit(frame_copy)
            self.result.emit(result)


class YoloDetect(QObject):

    def __init__(self, model):
        QObject.__init__(self)
        self.detector = Detector('model/'+model, 'cpu', 0)


    def detect(self, frame):
    
        # frame_org = frame
        # frame = cv2.resize(frame, (int(852), int(480)))
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

        # 绘制矩形框
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # 绘制标签
        cv2.putText(frame, str(label_id), (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

class SegmentDetect(QObject):
    
    # image = Signal(np.ndarray)
    # result = Signal(np.ndarray)

    def __init__(self, model):
        QObject.__init__(self)
        self.seg_detector = Segmentor('model/'+model, 'cpu', 0)
    
    def detect(self, frame):
        # frame_org = frame
        seg = self.seg_detector(frame)

        print(seg.shape)

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

        return frame
        # self.image.emit(frame_org)
        # self.result.emit(frame)
    
    def get_palette(self, num_classes=256):
        state = np.random.get_state()
        # random color
        np.random.seed(42)
        palette = np.random.randint(0, 256, size=(num_classes, 3))
        np.random.set_state(state)
        return [tuple(c) for c in palette]
    

class PoseDetect(QObject):

    def __init__(self, model):
        QObject.__init__(self)
        self.detector = Detector('model/yolov8', 'cpu', 0)
        self.pose_detector = PoseDetector('model/pose', 'cpu', 0)

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


class MainWindow(QMainWindow):
    
    begin = Signal()
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.label_1 = self.ui.label_1
        self.label_2 = self.ui.label_2
        self.model_selector = self.ui.model
        self.slide_bar = self.ui.horizontalSlider
        self.play_button = self.ui.playButton

        self.play_button.clicked.connect(self.play)
        # 读取model目录项的目录名
        self.model_dir = os.listdir('model')
        print(self.model_dir)

        # 设置model_selector的选项
        self.model_selector.addItems(self.model_dir)
        self.model_selector.setCurrentIndex(0)
        self.model_selector.currentTextChanged.connect(self.text_changed)

        self.detector_thread = QThread()

    def text_changed(self):
        model = self.model_selector.currentText()

        if model == 'yolov8':
                self.detector = YoloDetect(model)
        elif model == 'seg':
                self.detector = SegmentDetect(model)
        elif model == 'pose':
                self.detector = PoseDetect(model)

        if not self.detector_thread.isRunning():

            self.videoPlayer = VideoPlayer('04.mp4')
            self.videoPlayer.set_detector(self.detector)
        
            self.videoPlayer.image.connect(lambda x: self.show_image(x, self.label_1))
            self.videoPlayer.result.connect(lambda x: self.show_image(x, self.label_2))
            self.videoPlayer.progress_slider.connect(lambda x: self.slide_bar.setValue(x))

            self.slide_bar.sliderPressed.connect(self.stop_play)
            self.slide_bar.sliderReleased.connect(self.set_frame)

            self.begin.connect(self.videoPlayer.playVideo)

            self.videoPlayer.moveToThread(self.detector_thread)
            self.detector_thread.start()
        else:
            self.videoPlayer.set_detector(self.detector)
            self.videoPlayer.image.connect(lambda x: self.show_image(x, self.label_1))
            self.videoPlayer.result.connect(lambda x: self.show_image(x, self.label_2))
    

    def set_frame(self):
        self.videoPlayer.set_play_status(True)
        self.videoPlayer.set_frame(self.slide_bar.value())
        self.begin.emit()

    def play(self):
        play_status = self.videoPlayer.get_play_status()
        if play_status == False:    
            self.videoPlayer.set_play_status(True)
            self.begin.emit()
            self.play_button.setText('暂停')
        else:
            self.videoPlayer.set_play_status(False)
            self.play_button.setText('播放')

    def stop_play(self):
        self.videoPlayer.set_play_status(False)

    @staticmethod
    def set_progress(value, progress_bar):
        progress_bar.setValue(value)

    def closeEvent(self, event):
        if self.detector_thread.isRunning:
            self.detector_thread.terminate()
            self.detector_thread.wait()
            self.videoPlayer.cap.release()
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