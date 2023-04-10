from PySide6.QtWidgets import QMainWindow, QApplication, QMenu, QHBoxLayout, QLabel
from widgets.VideoPlayerTableWidget import VideoPlayerTableWidget
import sys
import os
from ui.grid_main import Ui_MainWindow
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

from widgets.VsrAnalysisWidget import VsrAnalysisWidget

class MainWindow(QMainWindow):
    
  def __init__(self, parent=None):
    super(MainWindow, self).__init__(parent)

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # 获取stackedWidget
    self.stack_widget = self.ui.stackedWidget
    self.stack_widget.setContentsMargins(0, 0, 0, 0)

    # 设置 page1 为视频播放页面
    self.playerPage = self.ui.page
    self.videoPlayerTableWidget = VideoPlayerTableWidget(2, 2, self.playerPage)
    self.playerPage.setLayout(QHBoxLayout())
    self.playerPage.layout().addWidget(self.videoPlayerTableWidget)

    # 设置 page2 为图片超分辨率页面
    self.vsr_page = self.ui.page_2
    self.horizontalLayout = self.ui.horizontalLayout_2
    self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
    self.horizontalLayout.setSpacing(1)
    vsrAnalysisWidget = VsrAnalysisWidget(self.vsr_page)
    self.horizontalLayout.addWidget(vsrAnalysisWidget)

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
    # 绑定菜单项事件
    self.action1x1.triggered.connect(lambda: self.videoPlayerTableWidget.change_grid_size(1,1))
    self.action2x2.triggered.connect(lambda: self.videoPlayerTableWidget.change_grid_size(2,2))
    self.action4x4.triggered.connect(lambda: self.videoPlayerTableWidget.change_grid_size(4,4))

    # # 设置窗口标题
    self.setWindowTitle("视频分析软件")
    # # 设置窗口大小
    self.resize(1920, 1080)

    # 获取左侧导航栏按钮
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

  def resizeEvent(self, event):
    # 获取vsr_page 中label的控件
    self.label = self.vsr_page.findChild(QLabel, "label")
    print(self.label.geometry())

  def closeEvent(self, event):
    event.accept()
    os._exit(0)

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())