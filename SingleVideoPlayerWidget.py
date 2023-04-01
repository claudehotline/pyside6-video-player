import os
import sys

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QFileDialog, QWidget, QApplication
from ui.single_video_player_widget import Ui_Form

from player.OpencvVideoPlayer import OpencvVideoPlayer
from player.SingleOpencvVideoPlayer import SingleOpencvVideoPlayer
from analyzer.PoseDetector import PoseDetect
from analyzer.Segmentor import Segment
from analyzer.YoloDetector import YoloDetector


class SingleVideoPlayerWidget(QWidget):
    
    begin = Signal()
    
    def __init__(self, parent=None):
        super(SingleVideoPlayerWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    

        self.label = self.ui.label
        

        # 检测类别选择器
        self.detectType_selector = self.ui.detectType
        self.detectType_selector.addItems(['目标检测', '语义分割', '人体姿态'])
        self.detectType_selector.show()
        self.detectType_selector.currentTextChanged.connect(self.detectType_changed)

        # 模型选择器
        self.model_selector = self.ui.model
        self.model_selector.hide()
        self.model_selector.currentTextChanged.connect(self.model_changed)

        # 视频来源选择器
        self.videoSource_selector = self.ui.videoSource
        self.videoSource_selector.addItems(['本地视频', '网络视频', '本地摄像头'])
        self.videoSource_selector.hide()
        self.videoSource_selector.currentTextChanged.connect(self.videoSource_changed)

        # 选择视频文件按钮
        self.video_dialog_button = self.ui.videoDialogButton
        self.video_dialog_button.hide()
        self.video_dialog_button.clicked.connect(self.open_video_dialog)
        self.file_dialog = QFileDialog()

        # 摄像头选择器
        self.camera_selector = self.ui.camList
        self.camera_selector.hide()

        # 网络视频地址
        self.net_video_url = self.ui.videoUrlInput
        self.net_video_url.hide()
        self.net_video_url.returnPressed.connect(self.set_net_video_url)

        # 播放进度条
        self.slide_bar = self.ui.horizontalSlider

        # 播放/暂停按钮
        self.play_button = self.ui.playButton
        self.play_button.clicked.connect(self.play)

        self.videoPlayer = None
        self.detector_thread = QThread()


    def detectType_changed(self):
        self.detectType = self.detectType_selector.currentText()

        if self.detectType == '目标检测':
            self.model_list = os.listdir('model/detect')
        elif self.detectType == '语义分割':
            self.model_list = os.listdir('model/seg')
        elif self.detectType == '人体姿态':
            self.model_list = os.listdir('model/pose')

        self.model_selector.clear()
        self.model_selector.addItems(self.model_list)

        self.model_selector.show()
        

    def model_changed(self):
        model = self.model_selector.currentText()

        if self.detectType == '目标检测':
            self.detector = YoloDetector('model/detect' + os.path.sep + model)
        elif self.detectType == '语义分割':
            self.detector = Segment('model/seg' + os.path.sep + model)
        elif self.detectType == '人体姿态':
            self.detector = PoseDetect('model/pose' + os.path.sep + model)

        self.videoSource_selector.show()

        # if not self.videoPlayer.videoFrameReaderThread.isRunning():
        if not self.videoPlayer:

            self.videoPlayer = OpencvVideoPlayer()
            self.videoPlayer.set_detector(self.detector)
        
            # self.videoPlayer.image.connect(lambda x: self.show_image(x, self.label))
            self.videoPlayer.videoFrameProcessor.result.connect(lambda x: self.show_image(x, self.label))
            self.videoPlayer.progress_slider.connect(lambda x: self.slide_bar.setValue(x))

            self.slide_bar.sliderPressed.connect(self.stop_play)
            self.slide_bar.sliderReleased.connect(self.set_frame)

            self.begin.connect(self.videoPlayer.playVideo2)

            self.videoPlayer.moveToThread(self.detector_thread)
            self.detector_thread.start()
        else:
            self.videoPlayer.set_detector(self.detector)
            # self.videoPlayer.image.connect(lambda x: self.show_image(x, self.label_1))
            self.videoPlayer.result.connect(lambda x: self.show_image(x, self.label))


    def videoSource_changed(self):
        videoSource = self.videoSource_selector.currentText()

        if videoSource == '本地视频':
            self.video_dialog_button.show()
            self.camera_selector.hide()
            self.net_video_url.hide()
        elif videoSource == '网络视频':
            self.video_dialog_button.hide()
            self.camera_selector.hide()
            self.net_video_url.show()
        elif videoSource == '本地摄像头':
            self.video_dialog_button.hide()
            self.camera_selector.show()
            self.net_video_url.hide()

    def set_net_video_url(self):
        self.videoPlayer.set_video(self.net_video_url.text())

    # def text_changed(self):
        # model = self.model_selector.currentText()

        # if model == 'yolov8m_trt':
        #     self.detector = YoloDetector(model)
        # elif model == 'unet_trt':
        #     self.detector = Segment(model)
        # elif model == 'hrnet_trt':
        #     self.detector = PoseDetect(model)

        
    

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
        label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        event.accept()
        os._exit(0)

if __name__ == "__main__":
    app = QApplication([])
    window = SingleVideoPlayerWidget()
    window.show()
    sys.exit(app.exec())