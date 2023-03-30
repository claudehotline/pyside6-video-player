from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QGridLayout
from widgets.VideoPlayerWidget import VideoPlayerWidget
from widgets.SingleVideoPlayerWidget import SingleVideoPlayerWidget
import sys

class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # self.videoPlayerWidget1 = SingleVideoPlayerWidget(self)
        # self.videoPlayerWidget2 = SingleVideoPlayerWidget(self)
        # self.videoPlayerWidget3 = SingleVideoPlayerWidget(self)
        # self.videoPlayerWidget4 = SingleVideoPlayerWidget(self)
        # 创建GridLayout
        grid = QGridLayout()
        row = 4
        col = 4
        self.videoPlayerWidgetList = []
        for i in range(row * col):
            self.videoPlayerWidget = SingleVideoPlayerWidget(self)
            grid.addWidget(self.videoPlayerWidget, i//4, i%4)
            self.videoPlayerWidgetList.append(self.videoPlayerWidget)
        # # 创建一个widget
        widget = QWidget()
        # # 设置布局
        widget.setLayout(grid)
        # # 设置中心窗口
        self.setCentralWidget(widget)
        # # 设置窗口标题
        self.setWindowTitle("视频分析软件")
        # # 设置窗口大小
        self.resize(1920, 1080)

    def closeEvent(self, event):
        for w in self.videoPlayerWidgetList:
            w.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())