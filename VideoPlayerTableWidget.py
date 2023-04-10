from PySide6.QtWidgets import QWidget, QGridLayout, QApplication
from widgets.SingleVideoPlayerWidget import SingleVideoPlayerWidget

import os
import sys


class VideoPlayerTableWidget(QWidget):
    
    def __init__(self, row, col, parent=None):
        super(VideoPlayerTableWidget, self).__init__(parent)

        self.row = row
        self.col = col

        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(1)

        self.videoPlayerWidgetList = []
        for i in range(self.row * self.col):
          self.videoPlayerWidget = SingleVideoPlayerWidget(self)
          self.videoPlayerWidget.setContentsMargins(0, 0, 0, 0)
          self.grid.addWidget(self.videoPlayerWidget, i//self.row, i%self.col)
          self.videoPlayerWidgetList.append(self.videoPlayerWidget)

    def change_grid_size(self, row, col):
      for i in range(len(self.videoPlayerWidgetList)):
        self.grid.removeWidget(self.videoPlayerWidgetList[i])
        if self.videoPlayerWidgetList[i].videoPlayer != None:
          self.videoPlayerWidgetList[i].release()
        self.videoPlayerWidgetList[i].deleteLater()
      self.videoPlayerWidgetList = []

      for i in range(row * col):
        self.videoPlayerWidget = SingleVideoPlayerWidget(self)
        self.grid.addWidget(self.videoPlayerWidget, i//row, i%col)
        self.videoPlayerWidgetList.append(self.videoPlayerWidget)

    def closeEvent(self, event):
      event.accept()
      os._exit(0)

if __name__ == "__main__":
    app = QApplication([])
    window = VideoPlayerTableWidget(2, 2)
    VideoPlayerTableWidget.change_grid_size(window, 4, 4)
    # 设置window的大小
    window.resize(1920, 1080)
    window.show()
    sys.exit(app.exec())