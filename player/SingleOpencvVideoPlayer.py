from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QApplication
from ui.single_video_player_widget import Ui_Form
from widgets.PlayerSettingDialog import PlayerSettingDialog
from player.VideoPlayer import VideoPlayer
from player.transport.TransportVideoPlayer import TransportVideoPlayer


class SingleVideoPlayerWidget(QWidget):
    
    begin = Signal()
    
    def __init__(self, parent=None):
        super(SingleVideoPlayerWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    

        self.label = self.ui.label

        # 选择视频文件按钮
        self.video_dialog_button = self.ui.playerSettingBtn
        self.video_dialog_button.clicked.connect(self.show_player_setting_dialog)

        # 播放进度条
        self.slide_bar = self.ui.horizontalSlider

        # 播放/暂停按钮
        self.play_button = self.ui.playButton
        self.play_button.clicked.connect(self.play)

        # self.videoPlayer = VideoPlayer()
        # self.videoPlayer = TransportVideoPlayer()
        self.videoPlayer = None
        self.videoPlayer_thread = None
        # self.begin.connect(self.videoPlayer.playVideo)
        # self.videoPlayer.moveToThread(self.videoPlayer_thread)
        # self.videoPlayer_thread.start()


    def show_player_setting_dialog(self):
        self.player_setting_dialog = PlayerSettingDialog()
        self.player_setting_dialog.show()
        self.player_setting_dialog.settings.connect(lambda detectType, model_list, video_path: self.videoPlayer.set_player(detectType, model_list, video_path))


    def set_video_player(self, videoPlayer):
        self.videoPlayer = videoPlayer
        self.videoPlayer_thread = QThread()
        self.begin.connect(self.videoPlayer.playVideo)
        self.videoPlayer.moveToThread(self.videoPlayer_thread)
        self.videoPlayer_thread.start()

    def set_frame(self):
        self.videoPlayer.set_play_status(True)
        self.videoPlayer.set_frame(self.slide_bar.value())
        self.begin.emit()

    def play(self):
        play_status = self.videoPlayer.get_play_status()
        play_is_setting_done = self.videoPlayer.get_setting_status()
        if play_status == False and play_is_setting_done:    
            self.videoPlayer.set_play_status(True)
            self.videoPlayer.get_video_frame_processor().result.connect(lambda result: self.show_image(result, self.label))
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

    @staticmethod
    def show_image(img_src, label):
        image = QImage(img_src, img_src.shape[1], img_src.shape[0], QImage.Format_BGR888)
        image = image.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(QPixmap.fromImage(image))

    def release(self):
        if self.detector_thread.isRunning:
            self.detector_thread.terminate()
            self.detector_thread.wait()
            self.videoPlayer.cap.release()

    # def closeEvent(self, event):
    #     event.accept()
    #     os._exit(0)