# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'readfull_gui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_readWidget(object):
    def setupUi(self, readWidget):
        if not readWidget.objectName():
            readWidget.setObjectName(u"readWidget")
        readWidget.resize(402, 168)
        self.gridLayout_2 = QGridLayout(readWidget)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 9, -1, 8)
        self.horizontalLayout = QHBoxLayout()
#ifndef Q_OS_MAC
        self.horizontalLayout.setSpacing(-1)
#endif
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.startBtn = QPushButton(readWidget)
        self.startBtn.setObjectName(u"startBtn")

        self.horizontalLayout.addWidget(self.startBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.closeBtn = QPushButton(readWidget)
        self.closeBtn.setObjectName(u"closeBtn")

        self.horizontalLayout.addWidget(self.closeBtn)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(readWidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout.addWidget(self.label_2)

        self.DumpGPTCheckbox = QCheckBox(readWidget)
        self.DumpGPTCheckbox.setObjectName(u"DumpGPTCheckbox")

        self.verticalLayout.addWidget(self.DumpGPTCheckbox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.progressText = QLabel(readWidget)
        self.progressText.setObjectName(u"progressText")

        self.verticalLayout.addWidget(self.progressText)

        self.progress = QProgressBar(readWidget)
        self.progress.setObjectName(u"progress")
        self.progress.setMaximumSize(QSize(16777215, 100))
        self.progress.setValue(0)

        self.verticalLayout.addWidget(self.progress)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(readWidget)

        QMetaObject.connectSlotsByName(readWidget)
    # setupUi

    def retranslateUi(self, readWidget):
        readWidget.setWindowTitle(QCoreApplication.translate("readWidget", u"Read full flash", None))
        self.startBtn.setText(QCoreApplication.translate("readWidget", u"Start", None))
        self.closeBtn.setText(QCoreApplication.translate("readWidget", u"Close", None))
        self.label_2.setText(QCoreApplication.translate("readWidget", u"Select options", None))
        self.DumpGPTCheckbox.setText(QCoreApplication.translate("readWidget", u"Dump GPT", None))
        self.progressText.setText(QCoreApplication.translate("readWidget", u"Ready to start...", None))
    # retranslateUi

