from PySide6.QtWidgets import QFileDialog, QWidget, QApplication
from PySide6.QtCore import Signal
from ui.player_setting_dialog import Ui_Dialog
import os


class PlayerSettingDialog(QWidget):

    settings = Signal(str, list, str)

    def __init__(self, parent=None):
        super(PlayerSettingDialog, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.video_path = None
        self.detectType = None
        self.model_list = []

        # 检测类别单选按钮组
        self.detection_radio_button = self.ui.detection
        self.detection_radio_button.setChecked(True)
        self.detectType = self.detection_radio_button.text()
        self.detection_radio_button.toggled.connect(self.detection_radio_button_toggled)
        self.segmentation_radio_button = self.ui.segmentation
        self.segmentation_radio_button.toggled.connect(self.segmentation_radio_button_toggled)
        self.pose_radio_button = self.ui.poseRecognition
        self.pose_radio_button.toggled.connect(self.pose_radio_button_toggled)

        # 模型选择器
        self.model1_selector = self.ui.model1
        self.model1_list = os.listdir('model/detect')
        self.model1_selector.addItems(self.model1_list)
        self.model2_selector = self.ui.model2
        
        # 视频来源单选按钮组
        self.local_video_file_radio_button = self.ui.localFile
        self.local_video_file_radio_button.setChecked(True)
        self.local_video_file_radio_button.toggled.connect(self.local_video_file_radio_button_toggled)
        self.local_cam_radio_button = self.ui.localCam
        self.local_cam_radio_button.toggled.connect(self.local_cam_radio_button_toggled)
        self.net_video_radio_button = self.ui.netUrl
        self.net_video_radio_button.toggled.connect(self.net_video_radio_button_toggled)

        # 选择视频文件按钮
        self.file_dialog_button = self.ui.FileDialogBtn
        self.file_dialog_button.clicked.connect(self.open_video_dialog)
        self.file_dialog = QFileDialog()
        # 摄像头选择器
        self.local_cam_selector = self.ui.localCamSelector
        self.local_cam_selector.setDisabled(True)
        # 网络视频地址输入框
        self.net_video_url_input = self.ui.netUrlInput
        self.net_video_url_input.setDisabled(True)

        self.buttonBox = self.ui.buttonBox
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


    def detection_radio_button_toggled(self):
        self.model1_list = os.listdir('model/detect')
        self.model1_selector.clear()
        self.model1_selector.addItems(self.model1_list)
        self.detectType = self.detection_radio_button.text()

    def segmentation_radio_button_toggled(self):
        self.model1_list = os.listdir('model/seg')
        self.model1_selector.clear()
        self.model1_selector.addItems(self.model1_list)
        self.detectType = self.segmentation_radio_button.text()

    def pose_radio_button_toggled(self):
        self.model1_list = os.listdir('model/detect')
        self.model1_selector.clear()
        self.model1_selector.addItems(self.model1_list)
        self.model2_list = os.listdir('model/pose')
        self.model2_selector.clear()
        self.model2_selector.addItems(self.model2_list)
        self.detectType = self.pose_radio_button.text()

    def local_video_file_radio_button_toggled(self):
        self.local_cam_selector.setDisabled(True)
        self.net_video_url_input.setDisabled(True)
        self.file_dialog_button.setDisabled(False)

    def local_cam_radio_button_toggled(self):
        self.local_cam_selector.setDisabled(False)
        self.net_video_url_input.setDisabled(True)
        self.file_dialog_button.setDisabled(True)

    def net_video_radio_button_toggled(self):
        self.local_cam_selector.setDisabled(True)
        self.net_video_url_input.setDisabled(False)
        self.file_dialog_button.setDisabled(True)


    def open_video_dialog(self):
        self.video_path, _ = self.file_dialog.getOpenFileName(
            self,
            '选择视频文件',
            'video',
            self.file_dialog.setNameFilter('视频文件(*.mp4 *.avi *.mov *.mkv)')
        )

    def accept(self):
        self.model_list.append(self.model1_selector.currentText())
        self.model_list.append(self.model2_selector.currentText())
        if self.local_video_file_radio_button.isChecked():
            self.video_path = self.video_path
        elif self.local_cam_radio_button.isChecked():
            self.video_path = self.local_cam_selector.currentText()
        elif self.net_video_radio_button.isChecked():
            self.video_path = self.net_video_url_input.text()

        self.settings.emit(self.detectType, self.model_list, self.video_path)

        print('accept')
        self.close()
    
    def reject(self):
        print('reject')
        self.close()