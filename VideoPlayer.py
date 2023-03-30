import cv2
from PySide6 import QtCore, QtGui, QtWidgets
from mmdeploy_python import Detector
 
class VideoPlayer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(VideoPlayer, self).__init__(parent)
        self.image_label = QtWidgets.QLabel()
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
 
        self.quit_button = QtWidgets.QPushButton("退出")
 
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.quit_button)
        self.setLayout(self.layout)
 
        self.quit_button.clicked.connect(self.close)
 
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.play)
        self.timer.start(1)
 
        self.capture = cv2.VideoCapture('01.mp4')

 
    def play(self):
        ret, frame = self.capture.read()
        print(ret, frame)
        if ret:
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))

            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(img)
            self.image_label.setPixmap(pix)

 
if __name__ == "__main__":
    import sys
 
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.play()
    player.show()
    sys.exit(app.exec_())