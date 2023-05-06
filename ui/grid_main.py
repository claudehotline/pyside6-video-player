# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'grid_main.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSlider, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(962, 682)
        MainWindow.setMaximumSize(QSize(16777215, 16777215))
        self.close = QAction(MainWindow)
        self.close.setObjectName(u"close")
        self.action1x1 = QAction(MainWindow)
        self.action1x1.setObjectName(u"action1x1")
        self.action2x2 = QAction(MainWindow)
        self.action2x2.setObjectName(u"action2x2")
        self.action4x4 = QAction(MainWindow)
        self.action4x4.setObjectName(u"action4x4")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(60, 0))
        self.frame.setMaximumSize(QSize(60, 16777215))
        self.frame.setStyleSheet(u"background-color: rgb(61, 63, 91);")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.togglebox = QFrame(self.frame)
        self.togglebox.setObjectName(u"togglebox")
        self.togglebox.setMaximumSize(QSize(16777215, 45))
        self.togglebox.setFrameShape(QFrame.StyledPanel)
        self.togglebox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.togglebox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.togglebtn = QPushButton(self.togglebox)
        self.togglebtn.setObjectName(u"togglebtn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.togglebtn.sizePolicy().hasHeightForWidth())
        self.togglebtn.setSizePolicy(sizePolicy1)
        self.togglebtn.setMinimumSize(QSize(60, 45))

        self.verticalLayout_2.addWidget(self.togglebtn)


        self.verticalLayout.addWidget(self.togglebox)

        self.top_menu = QFrame(self.frame)
        self.top_menu.setObjectName(u"top_menu")
        self.top_menu.setMinimumSize(QSize(0, 0))
        self.top_menu.setFrameShape(QFrame.StyledPanel)
        self.top_menu.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.top_menu)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.home_btn = QPushButton(self.top_menu)
        self.home_btn.setObjectName(u"home_btn")
        self.home_btn.setMinimumSize(QSize(60, 45))

        self.verticalLayout_3.addWidget(self.home_btn)

        self.test1_btn = QPushButton(self.top_menu)
        self.test1_btn.setObjectName(u"test1_btn")
        self.test1_btn.setMinimumSize(QSize(60, 45))

        self.verticalLayout_3.addWidget(self.test1_btn)

        self.test2_btn = QPushButton(self.top_menu)
        self.test2_btn.setObjectName(u"test2_btn")
        self.test2_btn.setMinimumSize(QSize(60, 45))

        self.verticalLayout_3.addWidget(self.test2_btn)

        self.car_rec_btn = QPushButton(self.top_menu)
        self.car_rec_btn.setObjectName(u"car_rec_btn")
        self.car_rec_btn.setMinimumSize(QSize(60, 45))

        self.verticalLayout_3.addWidget(self.car_rec_btn)

        self.lane_btn = QPushButton(self.top_menu)
        self.lane_btn.setObjectName(u"lane_btn")
        self.lane_btn.setMinimumSize(QSize(60, 45))
        self.lane_btn.setMaximumSize(QSize(16777215, 16777215))

        self.verticalLayout_3.addWidget(self.lane_btn)


        self.verticalLayout.addWidget(self.top_menu, 0, Qt.AlignTop)

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_3)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.bottomExpbtn = QPushButton(self.frame_3)
        self.bottomExpbtn.setObjectName(u"bottomExpbtn")
        self.bottomExpbtn.setMinimumSize(QSize(60, 45))

        self.verticalLayout_4.addWidget(self.bottomExpbtn)

        self.pushButton_5 = QPushButton(self.frame_3)
        self.pushButton_5.setObjectName(u"pushButton_5")
        self.pushButton_5.setMinimumSize(QSize(60, 45))

        self.verticalLayout_4.addWidget(self.pushButton_5)


        self.verticalLayout.addWidget(self.frame_3, 0, Qt.AlignBottom)


        self.horizontalLayout.addWidget(self.frame)

        self.frame2 = QFrame(self.centralwidget)
        self.frame2.setObjectName(u"frame2")
        self.frame2.setStyleSheet(u"background-color: rgb(89, 89, 89);")
        self.frame2.setFrameShape(QFrame.StyledPanel)
        self.frame2.setFrameShadow(QFrame.Raised)
        self.frame2.setLineWidth(1)
        self.horizontalLayout_3 = QHBoxLayout(self.frame2)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.expand = QFrame(self.frame2)
        self.expand.setObjectName(u"expand")
        self.expand.setMinimumSize(QSize(0, 0))
        self.expand.setMaximumSize(QSize(0, 16777215))
        self.expand.setFrameShape(QFrame.StyledPanel)
        self.expand.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.expand)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.scoreFrame = QFrame(self.expand)
        self.scoreFrame.setObjectName(u"scoreFrame")
        self.scoreFrame.setFrameShape(QFrame.StyledPanel)
        self.scoreFrame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.scoreFrame)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.scoreFrame)
        self.label.setObjectName(u"label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)

        self.horizontalLayout_5.addWidget(self.label)

        self.scoreValue = QLabel(self.scoreFrame)
        self.scoreValue.setObjectName(u"scoreValue")

        self.horizontalLayout_5.addWidget(self.scoreValue)


        self.verticalLayout_5.addWidget(self.scoreFrame, 0, Qt.AlignTop)

        self.frame_2 = QFrame(self.expand)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.scoreSlider = QSlider(self.frame_2)
        self.scoreSlider.setObjectName(u"scoreSlider")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.scoreSlider.sizePolicy().hasHeightForWidth())
        self.scoreSlider.setSizePolicy(sizePolicy3)
        self.scoreSlider.setMaximumSize(QSize(16777215, 16777215))
        self.scoreSlider.setValue(30)
        self.scoreSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_4.addWidget(self.scoreSlider)


        self.verticalLayout_5.addWidget(self.frame_2)


        self.horizontalLayout_3.addWidget(self.expand, 0, Qt.AlignTop)

        self.stackedWidget = QStackedWidget(self.frame2)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setEnabled(True)
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.stackedWidget.setStyleSheet(u"background-color: rgb(61, 63, 91);")
        self.stackedWidget.setLineWidth(1)
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.gridLayout = QGridLayout(self.page)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.horizontalLayout_2 = QHBoxLayout(self.page_2)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget.addWidget(self.page_2)
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.stackedWidget.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.stackedWidget.addWidget(self.page_4)
        self.page_5 = QWidget()
        self.page_5.setObjectName(u"page_5")
        self.stackedWidget.addWidget(self.page_5)

        self.horizontalLayout_3.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.frame2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 962, 21))
        self.menubar.setStyleSheet(u"background-color: rgb(61, 63, 91);")
        self.file = QMenu(self.menubar)
        self.file.setObjectName(u"file")
        self.setting = QMenu(self.menubar)
        self.setting.setObjectName(u"setting")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setStyleSheet(u"background-color: rgb(61, 63, 91);")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.file.menuAction())
        self.menubar.addAction(self.setting.menuAction())
        self.file.addAction(self.close)
        self.setting.addAction(self.action1x1)
        self.setting.addAction(self.action2x2)
        self.setting.addAction(self.action4x4)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.close.setText(QCoreApplication.translate("MainWindow", u"\u5173\u95ed", None))
        self.action1x1.setText(QCoreApplication.translate("MainWindow", u"1x1", None))
        self.action2x2.setText(QCoreApplication.translate("MainWindow", u"2x2", None))
        self.action4x4.setText(QCoreApplication.translate("MainWindow", u"4x4", None))
        self.togglebtn.setText(QCoreApplication.translate("MainWindow", u"\u5c55\u5f00", None))
        self.home_btn.setText(QCoreApplication.translate("MainWindow", u"\u901a\u7528\u5206\u6790\n"
"\u6a21\u578b", None))
        self.test1_btn.setText(QCoreApplication.translate("MainWindow", u"\u8d85\u5206\u8fa8\u7387", None))
        self.test2_btn.setText(QCoreApplication.translate("MainWindow", u"\u8f66\u6d41\u91cf\n"
"\u7edf\u8ba1", None))
        self.car_rec_btn.setText(QCoreApplication.translate("MainWindow", u"\u8f66\u8f86\u8bc6\u522b", None))
        self.lane_btn.setText(QCoreApplication.translate("MainWindow", u"\u8f66\u9053\u7ebf\n"
"\u68c0\u6d4b", None))
        self.bottomExpbtn.setText(QCoreApplication.translate("MainWindow", u"push", None))
        self.pushButton_5.setText(QCoreApplication.translate("MainWindow", u"setting", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"score\u9608\u503c\uff1a", None))
        self.scoreValue.setText(QCoreApplication.translate("MainWindow", u"0.3", None))
        self.file.setTitle(QCoreApplication.translate("MainWindow", u"\u6587\u4ef6", None))
        self.setting.setTitle(QCoreApplication.translate("MainWindow", u"\u914d\u7f6e", None))
    # retranslateUi

