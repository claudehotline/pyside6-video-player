# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'single_video_player_widget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(781, 532)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.tools = QFrame(Form)
        self.tools.setObjectName(u"tools")
        self.tools.setMaximumSize(QSize(16777215, 20))
        self.horizontalLayout = QHBoxLayout(self.tools)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.detectType = QComboBox(self.tools)
        self.detectType.setObjectName(u"detectType")

        self.horizontalLayout.addWidget(self.detectType)

        self.model = QComboBox(self.tools)
        self.model.setObjectName(u"model")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.model.sizePolicy().hasHeightForWidth())
        self.model.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.model)

        self.videoSource = QComboBox(self.tools)
        self.videoSource.setObjectName(u"videoSource")

        self.horizontalLayout.addWidget(self.videoSource)

        self.videoDialogButton = QPushButton(self.tools)
        self.videoDialogButton.setObjectName(u"videoDialogButton")
        sizePolicy.setHeightForWidth(self.videoDialogButton.sizePolicy().hasHeightForWidth())
        self.videoDialogButton.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.videoDialogButton)

        self.camList = QComboBox(self.tools)
        self.camList.setObjectName(u"camList")

        self.horizontalLayout.addWidget(self.camList)

        self.videoUrlInput = QLineEdit(self.tools)
        self.videoUrlInput.setObjectName(u"videoUrlInput")

        self.horizontalLayout.addWidget(self.videoUrlInput)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.tools)

        self.display = QFrame(Form)
        self.display.setObjectName(u"display")
        self.horizontalLayout_2 = QHBoxLayout(self.display)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.display)
        self.label.setObjectName(u"label")
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.label)


        self.verticalLayout.addWidget(self.display)

        self.progress = QFrame(Form)
        self.progress.setObjectName(u"progress")
        self.progress.setMaximumSize(QSize(16777215, 25))
        self.horizontalLayout_3 = QHBoxLayout(self.progress)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.playButton = QPushButton(self.progress)
        self.playButton.setObjectName(u"playButton")
        sizePolicy.setHeightForWidth(self.playButton.sizePolicy().hasHeightForWidth())
        self.playButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.playButton)

        self.horizontalSlider = QSlider(self.progress)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout_3.addWidget(self.horizontalSlider)


        self.verticalLayout.addWidget(self.progress)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.detectType.setPlaceholderText(QCoreApplication.translate("Form", u"\u68c0\u6d4b\u7c7b\u522b", None))
        self.model.setPlaceholderText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6a21\u578b", None))
        self.videoSource.setPlaceholderText(QCoreApplication.translate("Form", u"\u89c6\u9891\u6765\u6e90", None))
        self.videoDialogButton.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u89c6\u9891\u6587\u4ef6", None))
        self.camList.setPlaceholderText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6444\u50cf\u5934", None))
        self.videoUrlInput.setPlaceholderText(QCoreApplication.translate("Form", u"\u8f93\u5165\u89c6\u9891\u6d41\u5730\u5740", None))
        self.label.setText("")
        self.playButton.setText(QCoreApplication.translate("Form", u"\u64ad\u653e", None))
    # retranslateUi

