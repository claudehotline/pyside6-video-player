import cv2
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from mmdeploy_python import Detector

class VideoPlayer(QWidget):
    def __init__(self, video_file):
        super().__init__()

        # 创建 VideoCapture 对象并指定要读取的视频文件路径
        self.cap = cv2.VideoCapture(video_file)

        # 获取视频的帧率、宽度和高度
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 创建 QLabel 显示视频帧
        self.label = QLabel(self)
        self.label.setMinimumSize(852, 480)

        # 创建 QTimer 更新视频帧
        self.timer = QTimer(self)
        self.timer.setInterval(int(1000 / self.fps))
        self.timer.timeout.connect(self.update_frame)
        self.timer.start()

        self.detector = Detector(model_path='model', device_name='cpu', device_id=0)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.resize(frame, (852, 480))
            bboxes, labels, _ = self.detector(frame)
            print(bboxes)
            # 使用阈值过滤推理结果，并绘制到原图中
            indices = [i for i in range(len(bboxes))]
            for index, bbox, label_id in zip(indices, bboxes, labels):
                [left, top, right, bottom], score = bbox[0:4].astype(int),  bbox[4]
                if score < 0.3:
                    continue
                print(bbox[0:4])
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0))
            # 将 OpenCV 图像转换为 PySide6 QImage
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(image))
        else:
            # 播放结束时停止计时器和关闭视频文件
            self.timer.stop()
            self.cap.release()

if __name__ == '__main__':
    app = QApplication([])
    player = VideoPlayer('02.mp4')
    player.show()
    app.exec_()