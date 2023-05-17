from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QFileDialog, QHBoxLayout
from ui.sot import Ui_Form
from widgets.SingleVideoPlayerWidget import SingleVideoPlayerWidget
# from player.VideoPlayer import VideoPlayer
from player.SotVideoPlayer import SotVideoPlayer

class SotWidget(QWidget):

    start_analysis = Signal()
    start_tracking = Signal()
    stop_tracking = Signal()
    add_target = Signal()

    
    def __init__(self, parent=None):
        super(SotWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    
        # 视频选择按钮
        self.videoSelectBtn = self.ui.videoSelectBtn
        self.videoSelectBtn.clicked.connect(self.open_pic_dialog)
        self.file_dialog = QFileDialog()

        # 开始追踪按钮
        self.startTrackingBtn = self.ui.startTrackBtn
        self.startTrackingBtn.clicked.connect(self.start_track)

        # 停止追踪按钮
        self.stopTrackingBtn = self.ui.stopTrackBtn
        self.stopTrackingBtn.clicked.connect(self.stop_track)

        # 添加追踪目标按钮
        self.addTargetBtn = self.ui.addTargetBtn
        self.addTargetBtn.clicked.connect(self.add_tracking_target)

        # 视频播放器
        self.videoFrame = self.ui.frame_4
        self.videoFrame.setLayout(QHBoxLayout())
        self.videoFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.videoWidget = SingleVideoPlayerWidget()
        self.videoWidget.set_video_player(SotVideoPlayer())
        self.videoFrame.layout().addWidget(self.videoWidget)
        self.videoWidget.set_setting_btn_visibility(False)
        # self.videoWidget.videoPlayer.send_car_count.connect(lambda up, down:self.update_car_count(up, down))

        self.start_tracking.connect(self.videoWidget.videoPlayer.start_tracking)
        self.stop_tracking.connect(self.videoWidget.videoPlayer.stop_tracking)
        self.add_target.connect(self.videoWidget.videoPlayer.add_target)

    @Slot()
    def start_track(self):
        self.start_tracking.emit()
    
    @Slot()
    def stop_track(self):
        self.stop_tracking.emit()

    @Slot()
    def add_tracking_target(self):
        self.add_target.emit()

    @Slot()
    def open_pic_dialog(self):
        self.video_path, _ = self.file_dialog.getOpenFileName(
            self,
            '选择视频文件',
            '.',
            self.file_dialog.setNameFilter('图像文件(*.mp4 *.avi *.mov *.mkv)')
        )
        self.videoWidget.videoPlayer.set_player('单目标追踪', ['yolov8', 'ckpt.t7'], self.video_path)