# from PySide6.QtCore import Qt, Signal, QThread, Slot
# from PySide6.QtGui import QImage, QPixmap
# from PySide6.QtWidgets import QWidget, QLabel, QFileDialog, QApplication
# from ui.vsr_page_widget import Ui_Form
# from analyzer.SuperResolutionAnalyzer import SuperResolutionAnalyzer

# import os
# import sys
# import cv2
# import numpy as np


# class VsrPageWidget(QWidget):
    
#   begin = Signal()
    
#   def __init__(self, parent=None):
#     super(VsrPageWidget, self).__init__(parent)
#     self.ui = Ui_Form()
#     self.ui.setupUi(self)
    

#     self.label = self.ui.label

#     self.picSelectButton = self.ui.pushButton
#     self.picSelectButton.clicked.connect(self.open_pic_dialog)
#     self.file_dialog = QFileDialog()

#     self.org_image_label = self.ui.org_image_label
#     self.result_image_label = self.ui.result_image_label

#   def open_pic_dialog(self):
#     self.pic_path, _ = self.file_dialog.getOpenFileName(
#       self,
#       '选择图片',
#       '.',
#       self.file_dialog.setNameFilter('图像文件(*.jpg *.png *.bmp *.gif)')
#     )
    
#     image_src = cv2.imread(self.pic_path)
#     image = QImage(image_src, image_src.shape[1], image_src.shape[0], QImage.Format_BGR888)
#     image = image.scaled(self.org_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
#     self.org_image_label.setPixmap(QPixmap.fromImage(image))

#     vsr = SuperResolutionAnalyzer('model/vsr/esrgan')

#     result = vsr.detect(image_src)
#     result = result[..., ::-1]
#     result = np.ascontiguousarray(result)
#     image2 = QImage(result, result.shape[1], result.shape[0], QImage.Format_BGR888)
#     image2 = image2.scaled(self.result_image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
#     self.result_image_label.setPixmap(QPixmap.fromImage(image2))

#   def closeEvent(self, event):
#     event.accept()
#     os._exit(0)

# if __name__ == "__main__":
#     app = QApplication([])
#     window = VsrPageWidget()
#     window.show()
#     sys.exit(app.exec())