# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'player_setting_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(387, 427)
        self.verticalLayout_7 = QVBoxLayout(Dialog)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.frame_8 = QFrame(Dialog)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.frame_8)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox = QGroupBox(self.frame_8)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMaximumSize(QSize(80, 16777215))
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frame_4)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 5, -1, -1)
        self.detectType = QLabel(self.frame_4)
        self.detectType.setObjectName(u"detectType")
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.detectType.sizePolicy().hasHeightForWidth())
        self.detectType.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.detectType, 0, Qt.AlignTop)


        self.horizontalLayout.addWidget(self.frame_4)

        self.frame_2 = QFrame(self.frame)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.gridLayout = QGridLayout(self.frame_2)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.detection = QRadioButton(self.frame_2)
        self.detection.setObjectName(u"detection")
        sizePolicy.setHeightForWidth(self.detection.sizePolicy().hasHeightForWidth())
        self.detection.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.detection, 0, 0, 1, 1)

        self.segmentation = QRadioButton(self.frame_2)
        self.segmentation.setObjectName(u"segmentation")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.segmentation.sizePolicy().hasHeightForWidth())
        self.segmentation.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.segmentation, 0, 1, 1, 1)

        self.poseRecognition = QRadioButton(self.frame_2)
        self.poseRecognition.setObjectName(u"poseRecognition")

        self.gridLayout.addWidget(self.poseRecognition, 0, 2, 1, 1)

        self.tracking = QRadioButton(self.frame_2)
        self.tracking.setObjectName(u"tracking")
        sizePolicy1.setHeightForWidth(self.tracking.sizePolicy().hasHeightForWidth())
        self.tracking.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.tracking, 1, 1, 1, 1)

        self.actionRecognition = QRadioButton(self.frame_2)
        self.actionRecognition.setObjectName(u"actionRecognition")
        sizePolicy.setHeightForWidth(self.actionRecognition.sizePolicy().hasHeightForWidth())
        self.actionRecognition.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.actionRecognition, 1, 0, 1, 1)


        self.horizontalLayout.addWidget(self.frame_2)


        self.verticalLayout_5.addWidget(self.frame)

        self.frame_3 = QFrame(self.groupBox)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.model1Label = QLabel(self.frame_3)
        self.model1Label.setObjectName(u"model1Label")

        self.horizontalLayout_2.addWidget(self.model1Label)

        self.model1 = QComboBox(self.frame_3)
        self.model1.setObjectName(u"model1")

        self.horizontalLayout_2.addWidget(self.model1)

        self.horizontalSpacer = QSpacerItem(50, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.model2Label = QLabel(self.frame_3)
        self.model2Label.setObjectName(u"model2Label")

        self.horizontalLayout_2.addWidget(self.model2Label)

        self.model2 = QComboBox(self.frame_3)
        self.model2.setObjectName(u"model2")

        self.horizontalLayout_2.addWidget(self.model2)


        self.verticalLayout_5.addWidget(self.frame_3)


        self.verticalLayout_4.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(self.frame_8)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.verticalLayout_6 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.frame_7 = QFrame(self.groupBox_2)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_7)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.frame_5 = QFrame(self.frame_7)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame_5)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.localFile = QRadioButton(self.frame_5)
        self.localFile.setObjectName(u"localFile")

        self.verticalLayout_2.addWidget(self.localFile)

        self.localCam = QRadioButton(self.frame_5)
        self.localCam.setObjectName(u"localCam")

        self.verticalLayout_2.addWidget(self.localCam)

        self.netUrl = QRadioButton(self.frame_5)
        self.netUrl.setObjectName(u"netUrl")

        self.verticalLayout_2.addWidget(self.netUrl)


        self.horizontalLayout_3.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.frame_7)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_6)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.FileDialogBtn = QPushButton(self.frame_6)
        self.FileDialogBtn.setObjectName(u"FileDialogBtn")
        sizePolicy1.setHeightForWidth(self.FileDialogBtn.sizePolicy().hasHeightForWidth())
        self.FileDialogBtn.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.FileDialogBtn, 0, Qt.AlignTop)

        self.localCamSelector = QComboBox(self.frame_6)
        self.localCamSelector.setObjectName(u"localCamSelector")
        sizePolicy1.setHeightForWidth(self.localCamSelector.sizePolicy().hasHeightForWidth())
        self.localCamSelector.setSizePolicy(sizePolicy1)

        self.verticalLayout_3.addWidget(self.localCamSelector, 0, Qt.AlignVCenter)

        self.netUrlInput = QLineEdit(self.frame_6)
        self.netUrlInput.setObjectName(u"netUrlInput")

        self.verticalLayout_3.addWidget(self.netUrlInput)


        self.horizontalLayout_3.addWidget(self.frame_6)


        self.verticalLayout_6.addWidget(self.frame_7)


        self.verticalLayout_4.addWidget(self.groupBox_2)

        self.buttonBox = QDialogButtonBox(self.frame_8)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout_4.addWidget(self.buttonBox)


        self.verticalLayout_7.addWidget(self.frame_8)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("Dialog", u"\u6a21\u578b\u8bbe\u7f6e", None))
        self.detectType.setText(QCoreApplication.translate("Dialog", u"\u68c0\u6d4b\u7c7b\u522b", None))
        self.detection.setText(QCoreApplication.translate("Dialog", u"\u76ee\u6807\u68c0\u6d4b", None))
        self.segmentation.setText(QCoreApplication.translate("Dialog", u"\u8bed\u4e49\u5206\u5272", None))
        self.poseRecognition.setText(QCoreApplication.translate("Dialog", u"\u59ff\u6001\u8bc6\u522b", None))
        self.tracking.setText(QCoreApplication.translate("Dialog", u"\u591a\u76ee\u6807\u8ffd\u8e2a", None))
        self.actionRecognition.setText(QCoreApplication.translate("Dialog", u"\u52a8\u4f5c\u7406\u89e3", None))
        self.model1Label.setText(QCoreApplication.translate("Dialog", u"\u9009\u62e9\u6a21\u578b", None))
        self.model2Label.setText(QCoreApplication.translate("Dialog", u"\u9009\u62e9\u6a21\u578b", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("Dialog", u"\u89c6\u9891\u8bbe\u7f6e", None))
        self.localFile.setText(QCoreApplication.translate("Dialog", u"\u672c\u5730\u89c6\u9891", None))
        self.localCam.setText(QCoreApplication.translate("Dialog", u"\u672c\u5730\u6444\u50cf\u5934", None))
        self.netUrl.setText(QCoreApplication.translate("Dialog", u"\u7f51\u7edc\u89c6\u9891", None))
        self.FileDialogBtn.setText(QCoreApplication.translate("Dialog", u"\u6253\u5f00\u6587\u4ef6", None))
    # retranslateUi

