from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from VideoPlayerWidget import VideoPlayerWidget
import sys

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        videoPlayerWidget1 = VideoPlayerWidget(self)
        videoPlayerWidget2 = VideoPlayerWidget(self)
        # 创建垂直布局
        layout = QVBoxLayout()
        # 添加控件
        layout.addWidget(videoPlayerWidget1)
        layout.addWidget(videoPlayerWidget2)
        # 创建一个widget
        widget = QWidget()
        # 设置布局
        widget.setLayout(layout)
        # 设置中心窗口
        self.setCentralWidget(widget)
        # 设置窗口标题
        self.setWindowTitle("视频分析软件")
        # 设置窗口大小
        self.resize(800, 600)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())