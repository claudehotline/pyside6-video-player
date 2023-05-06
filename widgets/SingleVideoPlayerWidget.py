from PySide6.QtCore import Qt, Signal, QThread, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QProgressBar, QLabel
from ui.single_video_player_widget import Ui_Form

from player.VideoPlayer import VideoPlayer
from player.transport.TransportVideoPlayer import TransportVideoPlayer
from widgets.PlayerSettingDialog import PlayerSettingDialog

import numpy as np


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
        self.slide_bar.sliderPressed.connect(self.stop_play)
        self.slide_bar.sliderReleased.connect(self.set_frame)
        

        # 播放/暂停按钮
        self.play_button = self.ui.playButton
        self.play_button.clicked.connect(self.play)

        # 停止按钮
        self.stop_button = self.ui.stopButton

        # 创建播放器对象
        self.videoPlayer = None
        # self.videoPlayer = TransportVideoPlayer()
        # print('Transport videoPlayer')
        # self.stop_button.clicked.connect(self.videoPlayer.release)
        # self.videoPlayer.stop.connect(self.stop)

        # # 创建播放器线程
        # self.videoPlayer_thread = QThread()
        # self.begin.connect(self.videoPlayer.playVideo)
        # self.videoPlayer.moveToThread(self.videoPlayer_thread)
        # # 启动播放器线程
        # self.videoPlayer_thread.start()

        # # 连接信号槽
        # self.videoPlayer.update_progress_bar.connect(lambda value: self.set_progress(value, self.slide_bar))

    def set_video_player(self, videoPlayer):
        self.videoPlayer = videoPlayer
        self.stop_button.clicked.connect(self.videoPlayer.release)
        self.videoPlayer.stop.connect(self.stop)

        # 创建播放器线程
        self.videoPlayer_thread = QThread()
        self.begin.connect(self.videoPlayer.playVideo)
        self.videoPlayer.moveToThread(self.videoPlayer_thread)
        # 启动播放器线程
        self.videoPlayer_thread.start()

        # 连接信号槽
        self.videoPlayer.update_progress_bar.connect(lambda value: self.set_progress(value, self.slide_bar))

    def set_setting_btn_visibility(self, visible):
        if visible:
            self.video_dialog_button.show()
        else:
            self.video_dialog_button.hide()

    @Slot()
    def show_player_setting_dialog(self):
        self.player_setting_dialog = PlayerSettingDialog()
        self.player_setting_dialog.show()
        self.player_setting_dialog.settings.connect(lambda detectType, model_list, video_path: self.videoPlayer.set_player(detectType, model_list, video_path))
    
    @Slot()
    def set_frame(self):
        self.videoPlayer.set_frame(self.slide_bar.value())
        self.begin.emit()

    @Slot()
    def play(self):
        play_status = self.videoPlayer.get_play_status()
        play_is_setting_done = self.videoPlayer.get_setting_status()
        if play_status == False and play_is_setting_done:
            print('play')
            if self.videoPlayer_thread.isRunning() == False:
                self.videoPlayer_thread.start()
            self.videoPlayer.set_play_status(True)
            self.videoPlayer.get_video_frame_processor().result.connect(lambda result: self.show_image(result, self.label))
            self.begin.emit()
            self.play_button.setText('暂停')
        else:
            self.videoPlayer.set_play_status(False)
            self.play_button.setText('播放')

    @Slot()
    def stop_play(self):
        self.videoPlayer.set_play_status(False)

    @Slot()
    def stop(self):
        self.play_button.setText('播放')
        # self.videoPlayer.set_play_status(False)
        self.videoPlayer.set_setting_status(False)
        # self.videoPlayer.set_frame(0)
        self.slide_bar.setValue(0)
        self.label.clear()

    @Slot(int, QProgressBar)
    @staticmethod
    def set_progress(value, slide_bar):
        slide_bar.setValue(value)

    @Slot(np.ndarray, QLabel)
    @staticmethod
    def show_image(img_src, label):
        image = QImage(img_src, img_src.shape[1], img_src.shape[0], QImage.Format_BGR888)
        image = image.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # image 在label上居中显示
        label.setAlignment(Qt.AlignCenter)
        label.setPixmap(QPixmap.fromImage(image))

    def release(self):
        if self.videoPlayer_thread.isRunning:
            self.videoPlayer.release()
            self.videoPlayer_thread.quit()
            self.videoPlayer_thread.wait()