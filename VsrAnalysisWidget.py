from PySide6.QtCore import Qt, Signal, QThread, Slot, QObject
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QWidget, QProgressBar, QLabel, QFileDialog, QApplication
from ui.vsr_widget import Ui_Form

from player.VideoPlayer import VideoPlayer
from widgets.PlayerSettingDialog import PlayerSettingDialog
from analyzer.EsrganAnalyzer import EsrganAnalyzer

import numpy as np
import cv2
import sys
import os

class VsrAnalyzer(QObject):

    result_image = Signal(np.ndarray)

    def __init__(self, model_path):
        QObject.__init__(self)
        self.analyzer = EsrganAnalyzer(model_path)
        self.image = None

    def set_image(self, image):
        self.image = image

    def run(self):
        result = self.analyzer.detect(self.image)
        self.result_image.emit(result)

class VsrAnalysisWidget(QWidget):

    start_analysis = Signal()
    
    def __init__(self, parent=None):
        super(VsrAnalysisWidget, self).__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.image_src = None
    
        self.pic_select_btn = self.ui.pushButton
        self.org_pic_label = self.ui.label
        self.result_pic_label = self.ui.label_2

        self.pic_select_btn.clicked.connect(self.open_video_dialog)
        self.file_dialog = QFileDialog()

        self.analyzer = VsrAnalyzer('model/vsr/esrgan')
        self.analyzer_thread = QThread()
        self.analyzer.moveToThread(self.analyzer_thread)
        self.start_analysis.connect(self.analyzer.run)
        self.analyzer.result_image.connect(lambda x: self.set_label_image(x, self.result_pic_label))
        self.analyzer_thread.start()
        

    @Slot()
    def open_video_dialog(self):
        self.pic_path, _ = self.file_dialog.getOpenFileName(
            self,
            '选择图像文件',
            '.',
            self.file_dialog.setNameFilter('图像文件(*.mp4 *.avi *.mov *.mkv)')
        )

        self.image_src = cv2.imread(self.pic_path)
        image = QImage(self.image_src, self.image_src.shape[1], self.image_src.shape[0], QImage.Format_BGR888)
        image = image.scaled(self.org_pic_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.org_pic_label.setPixmap(QPixmap.fromImage(image))

        self.analyzer.set_image(self.image_src)
        self.start_analysis.emit()


    @Slot(np.ndarray, QLabel)
    @staticmethod
    def set_label_image(image, label):
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_BGR888)
        image = image.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        event.accept()
        os._exit(0)

if __name__ == "__main__":
    app = QApplication([])
    window = VsrAnalysisWidget()
    window.show()
    sys.exit(app.exec())