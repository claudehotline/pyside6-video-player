# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'video_player_widget.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QSlider, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_videoPlayerWidget(object):
    def setupUi(self, videoPlayerWidget):
        if not videoPlayerWidget.objectName():
            videoPlayerWidget.setObjectName(u"videoPlayerWidget")
        videoPlayerWidget.resize(934, 579)
        self.verticalLayout = QVBoxLayout(videoPlayerWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.model = QComboBox(videoPlayerWidget)
        self.model.setObjectName(u"model")

        self.horizontalLayout_3.addWidget(self.model)

        self.videoDialogButton = QPushButton(videoPlayerWidget)
        self.videoDialogButton.setObjectName(u"videoDialogButton")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.videoDialogButton.sizePolicy().hasHeightForWidth())
        self.videoDialogButton.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.videoDialogButton)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_1 = QLabel(videoPlayerWidget)
        self.label_1.setObjectName(u"label_1")

        self.horizontalLayout_2.addWidget(self.label_1)

        self.label_2 = QLabel(videoPlayerWidget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_2.addWidget(self.label_2)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.playButton = QPushButton(videoPlayerWidget)
        self.playButton.setObjectName(u"playButton")

        self.horizontalLayout.addWidget(self.playButton)

        self.horizontalSlider = QSlider(videoPlayerWidget)
        self.horizontalSlider.setObjectName(u"horizontalSlider")
        self.horizontalSlider.setOrientation(Qt.Horizontal)

        self.horizontalLayout.addWidget(self.horizontalSlider)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 15)
        self.verticalLayout.setStretch(2, 1)

        self.retranslateUi(videoPlayerWidget)

        QMetaObject.connectSlotsByName(videoPlayerWidget)
    # setupUi

    def retranslateUi(self, videoPlayerWidget):
        videoPlayerWidget.setWindowTitle(QCoreApplication.translate("videoPlayerWidget", u"Form", None))
        self.videoDialogButton.setText(QCoreApplication.translate("videoPlayerWidget", u"\u9009\u62e9\u89c6\u9891\u6587\u4ef6", None))
        self.label_1.setText("")
        self.label_2.setText("")
        self.playButton.setText(QCoreApplication.translate("videoPlayerWidget", u"\u64ad\u653e", None))
    # retranslateUi

