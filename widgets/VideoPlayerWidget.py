import os

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QFileDialog, QWidget
from ui.video_player_widget import Ui_videoPlayerWidget

from player.OpencvVideoPlayer import OpencvVideoPlayer
from analyzer.PoseDetector import PoseDetect
from analyzer.Segmentor import Segment
from analyzer.YoloDetector import YoloDetector


class VideoPlayerWidget(QWidget):
    
    begin = Signal()
    
    def __init__(self, parent=None):
        super(VideoPlayerWidget, self).__init__(parent)
        self.ui = Ui_videoPlayerWidget()
        
        self.ui.setupUi(self)
    
        self.label_1 = self.ui.label_1
        self.label_2 = self.ui.label_2
        self.model_selector = self.ui.model

        # 创建一个QFileDialog对象
        self.file_dialog = QFileDialog()

        self.slide_bar = self.ui.horizontalSlider
        self.play_button = self.ui.playButton

        self.play_button.clicked.connect(self.play)
        self.video_dialog_button = self.ui.videoDialogButton
        self.video_dialog_button.clicked.connect(self.open_video_dialog)
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

        if model == 'yolov8m_trt':
            self.detector = YoloDetector(model)
        elif model == 'unet_trt':
            self.detector = Segment(model)
        elif model == 'hrnet_trt':
            self.detector = PoseDetect(model)

        if not self.detector_thread.isRunning():

            self.videoPlayer = OpencvVideoPlayer()
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

    def open_video_dialog(self):
        videoPath, _ = self.file_dialog.getOpenFileName(
            self,
            '选择视频文件',
            'video',
            self.file_dialog.setNameFilter('视频文件(*.mp4 *.avi *.mov *.mkv)')
        )

        self.videoPlayer.set_video(videoPath)

    @staticmethod
    def set_progress(value, progress_bar):
        progress_bar.setValue(value)

    def release(self):
        if self.detector_thread.isRunning:
            self.detector_thread.terminate()
            self.detector_thread.wait()
            self.videoPlayer.cap.release()

    @staticmethod
    def show_image(img_src, label):
        image = QImage(img_src, img_src.shape[1], img_src.shape[0], QImage.Format_BGR888)
        image = image.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # image = image.scaled(label.size(), Qt.SmoothTransformation)
        label.setPixmap(QPixmap.fromImage(image))