from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from VideoPlayerWidget import VideoPlayerWidget
import sys

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        videoPlayerWidget = VideoPlayerWidget(self)
        self.setCentralWidget(videoPlayerWidget)
        self.setWindowTitle("Video Player")
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())