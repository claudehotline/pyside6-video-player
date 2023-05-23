# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'depth_estimation.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(916, 584)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.videoSelectBtn = QPushButton(self.frame_2)
        self.videoSelectBtn.setObjectName(u"videoSelectBtn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.videoSelectBtn.sizePolicy().hasHeightForWidth())
        self.videoSelectBtn.setSizePolicy(sizePolicy1)

        self.horizontalLayout_2.addWidget(self.videoSelectBtn, 0, Qt.AlignLeft)

        self.startTrackBtn = QPushButton(self.frame_2)
        self.startTrackBtn.setObjectName(u"startTrackBtn")

        self.horizontalLayout_2.addWidget(self.startTrackBtn)

        self.stopTrackBtn = QPushButton(self.frame_2)
        self.stopTrackBtn.setObjectName(u"stopTrackBtn")

        self.horizontalLayout_2.addWidget(self.stopTrackBtn)

        self.addTargetBtn = QPushButton(self.frame_2)
        self.addTargetBtn.setObjectName(u"addTargetBtn")

        self.horizontalLayout_2.addWidget(self.addTargetBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.frame_4 = QFrame(self.frame_3)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_3.addWidget(self.frame_4)

        self.horizontalLayout_3.setStretch(0, 1)

        self.verticalLayout.addWidget(self.frame_3)


        self.horizontalLayout.addWidget(self.frame)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.videoSelectBtn.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u89c6\u9891", None))
        self.startTrackBtn.setText(QCoreApplication.translate("Form", u"\u5f00\u59cb\u8ffd\u8e2a", None))
        self.stopTrackBtn.setText(QCoreApplication.translate("Form", u"\u505c\u6b62\u8ffd\u8e2a", None))
        self.addTargetBtn.setText(QCoreApplication.translate("Form", u"\u6dfb\u52a0\u76ee\u6807", None))
    # retranslateUi

