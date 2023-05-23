from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QFileDialog, QHBoxLayout
from ui.depth_estimation import Ui_Form
# from widgets.SingleVideoPlayerWidget import SingleVideoPlayerWidget
from widgets.DoubleVideoPlayerWidget import DoubleVideoPlayerWidget
# from player.DepthEstimatePlayer import DepthEstimatePlayer
from player.VideoPlayer import VideoPlayer

class DepthEstimateWidget(QWidget):
    
    def __init__(self, parent=None):
        super(DepthEstimateWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    
        # 视频选择按钮
        self.videoSelectBtn = self.ui.videoSelectBtn
        self.videoSelectBtn.clicked.connect(self.open_pic_dialog)
        self.file_dialog = QFileDialog()

        # 视频播放器
        self.videoFrame = self.ui.frame_4
        self.videoFrame.setLayout(QHBoxLayout())
        self.videoFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.videoWidget = DoubleVideoPlayerWidget()
        self.videoWidget.set_video_player(VideoPlayer())
        self.videoFrame.layout().addWidget(self.videoWidget)
        self.videoWidget.set_setting_btn_visibility(False)


    @Slot()
    def open_pic_dialog(self):
        self.video_path, _ = self.file_dialog.getOpenFileName(
            self,
            '选择视频文件',
            '.',
            self.file_dialog.setNameFilter('视频文件(*.mp4 *.avi *.mov *.mkv)')
        )
        self.videoWidget.videoPlayer.set_player('深度估计', ['yolov8', 'ckpt.t7'], self.video_path)