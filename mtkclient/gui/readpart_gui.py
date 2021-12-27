# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'readpart_gui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_partitionListWidget(object):
    def setupUi(self, partitionListWidget):
        if not partitionListWidget.objectName():
            partitionListWidget.setObjectName(u"partitionListWidget")
        partitionListWidget.resize(402, 593)
        self.gridLayout = QGridLayout(partitionListWidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 8, -1, 8)
        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_2, 8, 0, 1, 1)

        self.partProgressText = QLabel(partitionListWidget)
        self.partProgressText.setObjectName(u"partProgressText")

        self.gridLayout.addWidget(self.partProgressText, 4, 0, 1, 1)

        self.partProgress = QProgressBar(partitionListWidget)
        self.partProgress.setObjectName(u"partProgress")
        self.partProgress.setValue(0)

        self.gridLayout.addWidget(self.partProgress, 5, 0, 1, 1)

        self.fullProgress = QProgressBar(partitionListWidget)
        self.fullProgress.setObjectName(u"fullProgress")
        self.fullProgress.setValue(0)

        self.gridLayout.addWidget(self.fullProgress, 7, 0, 1, 1)

        self.partitionList = QScrollArea(partitionListWidget)
        self.partitionList.setObjectName(u"partitionList")
        self.partitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.partitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.partitionList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.partitionList.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 376, 436))
        self.partitionList.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.partitionList, 2, 0, 1, 1)

        self.fullProgressText = QLabel(partitionListWidget)
        self.fullProgressText.setObjectName(u"fullProgressText")

        self.gridLayout.addWidget(self.fullProgressText, 6, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.startBtn = QPushButton(partitionListWidget)
        self.startBtn.setObjectName(u"startBtn")

        self.horizontalLayout.addWidget(self.startBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.closeBtn = QPushButton(partitionListWidget)
        self.closeBtn.setObjectName(u"closeBtn")

        self.horizontalLayout.addWidget(self.closeBtn)


        self.gridLayout.addLayout(self.horizontalLayout, 9, 0, 1, 1)

        self.title = QLabel(partitionListWidget)
        self.title.setObjectName(u"title")
        self.title.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.title, 0, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_3, 1, 0, 1, 1)


        self.retranslateUi(partitionListWidget)

        QMetaObject.connectSlotsByName(partitionListWidget)
    # setupUi

    def retranslateUi(self, partitionListWidget):
        partitionListWidget.setWindowTitle(QCoreApplication.translate("partitionListWidget", u"Read partition(s)", None))
        self.partProgressText.setText(QCoreApplication.translate("partitionListWidget", u"Ready to start...", None))
        self.fullProgressText.setText("")
        self.startBtn.setText(QCoreApplication.translate("partitionListWidget", u"Start", None))
        self.closeBtn.setText(QCoreApplication.translate("partitionListWidget", u"Close", None))
        self.title.setText(QCoreApplication.translate("partitionListWidget", u"Select partitions to read", None))
    # retranslateUi

