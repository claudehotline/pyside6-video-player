from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QFileDialog, QHBoxLayout
from ui.transport_monitoring import Ui_Form
from widgets.SingleVideoPlayerWidget import SingleVideoPlayerWidget
from player.TransportVideoPlayer import TransportVideoPlayer

class TransportMonitoringWidget(QWidget):

    start_analysis = Signal()
    
    def __init__(self, parent=None):
        super(TransportMonitoringWidget, self).__init__(parent)
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
        self.videoWidget = SingleVideoPlayerWidget()
        self.videoWidget.set_video_player(TransportVideoPlayer())
        self.videoFrame.layout().addWidget(self.videoWidget)
        self.videoWidget.set_setting_btn_visibility(False)
        self.videoWidget.videoPlayer.send_car_count.connect(lambda up, down:self.update_car_count(up, down))

        # 车辆统计标签
        self.upCarCountLabel = self.ui.upCarCountLabel
        self.downCarCountLabel = self.ui.downCarCountLabel

    @Slot()
    def open_pic_dialog(self):
        self.video_path, _ = self.file_dialog.getOpenFileName(
            self,
            '选择视频文件',
            '.',
            self.file_dialog.setNameFilter('图像文件(*.mp4 *.avi *.mov *.mkv)')
        )
        self.videoWidget.videoPlayer.set_player('车辆统计', ['yolov8', 'ckpt.t7'], self.video_path)
        # , 'ckpt.t7'

    @Slot(int, int)
    def update_car_count(self, up_count, down_count):
        self.upCarCountLabel.setText(str(up_count))
        self.downCarCountLabel.setText(str(down_count))