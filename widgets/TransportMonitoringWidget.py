from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget, QFileDialog, QHBoxLayout
from ui.transport_monitoring import Ui_Form
from widgets.SingleVideoPlayerWidget import SingleVideoPlayerWidget

class TransportMonitoringWidget(QWidget):

    start_analysis = Signal()
    
    def __init__(self, parent=None):
        super(TransportMonitoringWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
    
        self.videoSelectBtn = self.ui.videoSelectBtn

        self.videoSelectBtn.clicked.connect(self.open_pic_dialog)
        self.file_dialog = QFileDialog()

        self.videoFrame = self.ui.frame_4
        self.videoFrame.setLayout(QHBoxLayout())
        self.videoFrame.layout().setContentsMargins(0, 0, 0, 0)
        self.videoWidget = SingleVideoPlayerWidget()
        self.videoFrame.layout().addWidget(self.videoWidget)

        self.videoWidget.set_setting_btn_visibility(False)

    @Slot()
    def open_pic_dialog(self):
        self.video_path, _ = self.file_dialog.getOpenFileName(
            self,
            '选择视频文件',
            '.',
            self.file_dialog.setNameFilter('图像文件(*.mp4 *.avi *.mov *.mkv)')
        )
        self.videoWidget.videoPlayer.set_player('车辆统计', ['yolov8s_trt', 'ckpt.t7'], self.video_path)