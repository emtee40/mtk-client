# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'writepart_gui.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QGridLayout, QHBoxLayout,
    QLabel, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_writepartitionListWidget(object):
    def setupUi(self, writepartitionListWidget):
        if not writepartitionListWidget.objectName():
            writepartitionListWidget.setObjectName(u"writepartitionListWidget")
        writepartitionListWidget.resize(402, 593)
        self.gridLayout = QGridLayout(writepartitionListWidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 8, -1, 8)
        self.title = QLabel(writepartitionListWidget)
        self.title.setObjectName(u"title")
        self.title.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.title, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer, 4, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_2, 11, 0, 1, 1)

        self.fullProgress = QProgressBar(writepartitionListWidget)
        self.fullProgress.setObjectName(u"fullProgress")
        self.fullProgress.setValue(0)

        self.gridLayout.addWidget(self.fullProgress, 10, 0, 1, 1)

        self.fullProgressText = QLabel(writepartitionListWidget)
        self.fullProgressText.setObjectName(u"fullProgressText")

        self.gridLayout.addWidget(self.fullProgressText, 9, 0, 1, 1)

        self.partProgress = QProgressBar(writepartitionListWidget)
        self.partProgress.setObjectName(u"partProgress")
        self.partProgress.setValue(0)

        self.gridLayout.addWidget(self.partProgress, 8, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_3, 1, 0, 1, 1)

        self.partProgressText = QLabel(writepartitionListWidget)
        self.partProgressText.setObjectName(u"partProgressText")

        self.gridLayout.addWidget(self.partProgressText, 7, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.startBtn = QPushButton(writepartitionListWidget)
        self.startBtn.setObjectName(u"startBtn")

        self.horizontalLayout.addWidget(self.startBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.closeBtn = QPushButton(writepartitionListWidget)
        self.closeBtn.setObjectName(u"closeBtn")

        self.horizontalLayout.addWidget(self.closeBtn)


        self.gridLayout.addLayout(self.horizontalLayout, 12, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_4, 6, 0, 1, 1)

        self.partitionList = QScrollArea(writepartitionListWidget)
        self.partitionList.setObjectName(u"partitionList")
        self.partitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.partitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.partitionList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.partitionList.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 382, 387))
        self.partitionList.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.partitionList, 2, 0, 1, 1)

        self.selectfromdir = QPushButton(writepartitionListWidget)
        self.selectfromdir.setObjectName(u"selectfromdir")

        self.gridLayout.addWidget(self.selectfromdir, 5, 0, 1, 1)


        self.retranslateUi(writepartitionListWidget)

        QMetaObject.connectSlotsByName(writepartitionListWidget)
    # setupUi

    def retranslateUi(self, writepartitionListWidget):
        writepartitionListWidget.setWindowTitle(QCoreApplication.translate("writepartitionListWidget", u"Write partition(s)", None))
        self.title.setText(QCoreApplication.translate("writepartitionListWidget", u"Select partitions to write", None))
        self.fullProgressText.setText("")
        self.partProgressText.setText(QCoreApplication.translate("writepartitionListWidget", u"Ready to start...", None))
        self.startBtn.setText(QCoreApplication.translate("writepartitionListWidget", u"Start", None))
        self.closeBtn.setText(QCoreApplication.translate("writepartitionListWidget", u"Close", None))
        self.selectfromdir.setText(QCoreApplication.translate("writepartitionListWidget", u"Select from directory", None))
    # retranslateUi

