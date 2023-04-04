from PySide6.QtWidgets import QMainWindow, QApplication, QMenu
from widgets.SingleVideoPlayerWidget import SingleVideoPlayerWidget
import sys
import os
from ui.grid_main import Ui_MainWindow
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

class MainWindow(QMainWindow):
    
  def __init__(self, parent=None):
    super(MainWindow, self).__init__(parent)

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.grid = self.ui.gridLayout
    self.row = 2
    self.col = 2
    self.videoPlayerWidgetList = []
    for i in range(self.row * self.col):
      self.videoPlayerWidget = SingleVideoPlayerWidget(self)
      self.grid.addWidget(self.videoPlayerWidget, i//self.row, i%self.col)
      self.videoPlayerWidgetList.append(self.videoPlayerWidget)


    # 获取menuBar
    self.menuBar = self.ui.menubar
    # 获取setting菜单项
    self.setting = self.menuBar.findChild(QMenu, "setting")
    self.action1x1 = None
    self.action2x2 = None
    self.action4x4 = None
    for action in self.setting.actions():
        if action.text() == "1x1":
            self.action1x1 = action
        elif action.text() == "2x2":
            self.action2x2 = action
        elif action.text() == "4x4":
            self.action4x4 = action
    # 绑定事件
    self.action1x1.triggered.connect(self.grid_change_1x1)
    self.action2x2.triggered.connect(self.grid_change_2x2)
    self.action4x4.triggered.connect(self.grid_change_4x4)

    # # 设置窗口标题
    self.setWindowTitle("视频分析软件")
    # # 设置窗口大小
    self.resize(1920, 1080)

    self.expanding_btn = self.ui.togglebtn
    self.expanding_btn.clicked.connect(self.expanding_menu)

    self.home_btn = self.ui.home_btn
    self.home_btn.clicked.connect(self.menuButtonClick)
    self.test1_btn = self.ui.test1_btn
    self.test1_btn.clicked.connect(self.menuButtonClick)
    self.test2_btn = self.ui.test2_btn
    self.test2_btn.clicked.connect(self.menuButtonClick)


  def menuButtonClick(self):
    btn = self.sender()
    btnName = btn.objectName()

    if btnName == "home_btn":
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

    if btnName == "test1_btn":
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)

    print(f'Button "{btnName}" pressed!')

  def expanding_menu(self):
    print('expanding_menu')
    width = self.ui.frame.width()
    print('width: ', width)
    maxExtend = 200
    standard = 60

    if width == 60:
        widthExtended = maxExtend
    else:
        widthExtended = standard
    
    # 设置动画
    self.animation = QPropertyAnimation(self.ui.frame, b"minimumWidth")
    self.animation.setDuration(400)
    self.animation.setStartValue(width)
    self.animation.setEndValue(widthExtended)
    self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    self.animation.start()


  def grid_change_1x1(self):
    for i in range(self.row * self.col):
      self.grid.removeWidget(self.videoPlayerWidgetList[i])
      if self.videoPlayerWidgetList[i].videoPlayer != None:
        self.videoPlayerWidgetList[i].release()
      self.videoPlayerWidgetList[i].deleteLater()
    self.videoPlayerWidgetList = []

    self.row = 1
    self.col = 1
    for i in range(self.row * self.col):
      self.videoPlayerWidget = SingleVideoPlayerWidget(self)
      self.grid.addWidget(self.videoPlayerWidget, i//self.row, i%self.col)
      self.videoPlayerWidgetList.append(self.videoPlayerWidget)

  def grid_change_2x2(self):
    for i in range(self.row * self.col):
        self.grid.removeWidget(self.videoPlayerWidgetList[i])
        if self.videoPlayerWidgetList[i].videoPlayer != None:
            self.videoPlayerWidgetList[i].release()
        self.videoPlayerWidgetList[i].deleteLater()
    self.videoPlayerWidgetList = []

    self.row = 2
    self.col = 2
    for i in range(self.row * self.col):
        self.videoPlayerWidget = SingleVideoPlayerWidget(self)
        self.grid.addWidget(self.videoPlayerWidget, i//self.row, i%self.col)
        self.videoPlayerWidgetList.append(self.videoPlayerWidget)
  
  def grid_change_4x4(self):
      for i in range(self.row * self.col):
          self.grid.removeWidget(self.videoPlayerWidgetList[i])
          if self.videoPlayerWidgetList[i].videoPlayer != None:
              self.videoPlayerWidgetList[i].release()
          self.videoPlayerWidgetList[i].deleteLater()
      self.videoPlayerWidgetList = []

      self.row = 4
      self.col = 4
      for i in range(self.row * self.col):
          self.videoPlayerWidget = SingleVideoPlayerWidget(self)
          self.grid.addWidget(self.videoPlayerWidget, i//self.row, i%self.col)
          self.videoPlayerWidgetList.append(self.videoPlayerWidget)

  def closeEvent(self, event):
    event.accept()
    os._exit(0)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())