# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'erasepart_gui.ui'
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
from PySide6.QtWidgets import (QAbstractScrollArea, QApplication, QCheckBox, QGridLayout,
    QHBoxLayout, QLabel, QProgressBar, QPushButton,
    QScrollArea, QSizePolicy, QSpacerItem, QWidget)

class Ui_partitionListWidget(object):
    def setupUi(self, partitionListWidget):
        if not partitionListWidget.objectName():
            partitionListWidget.setObjectName(u"partitionListWidget")
        partitionListWidget.resize(402, 593)
        self.gridLayout = QGridLayout(partitionListWidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(-1, 8, -1, 8)
        self.verticalSpacer_2 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_2, 10, 0, 1, 1)

        self.SelectAllCheckbox = QCheckBox(partitionListWidget)
        self.SelectAllCheckbox.setObjectName(u"SelectAllCheckbox")

        self.gridLayout.addWidget(self.SelectAllCheckbox, 4, 0, 1, 1)

        self.partProgress = QProgressBar(partitionListWidget)
        self.partProgress.setObjectName(u"partProgress")
        self.partProgress.setValue(0)

        self.gridLayout.addWidget(self.partProgress, 7, 0, 1, 1)

        self.fullProgress = QProgressBar(partitionListWidget)
        self.fullProgress.setObjectName(u"fullProgress")
        self.fullProgress.setValue(0)

        self.gridLayout.addWidget(self.fullProgress, 9, 0, 1, 1)

        self.fullProgressText = QLabel(partitionListWidget)
        self.fullProgressText.setObjectName(u"fullProgressText")

        self.gridLayout.addWidget(self.fullProgressText, 8, 0, 1, 1)

        self.partitionList = QScrollArea(partitionListWidget)
        self.partitionList.setObjectName(u"partitionList")
        self.partitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.partitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.partitionList.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.partitionList.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 382, 389))
        self.partitionList.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout.addWidget(self.partitionList, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)

        self.title = QLabel(partitionListWidget)
        self.title.setObjectName(u"title")
        self.title.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.gridLayout.addWidget(self.title, 0, 0, 1, 1)

        self.partProgressText = QLabel(partitionListWidget)
        self.partProgressText.setObjectName(u"partProgressText")

        self.gridLayout.addWidget(self.partProgressText, 6, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_3, 1, 0, 1, 1)

        self.verticalSpacer_4 = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.gridLayout.addItem(self.verticalSpacer_4, 5, 0, 1, 1)

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


        self.gridLayout.addLayout(self.horizontalLayout, 11, 0, 1, 1)


        self.retranslateUi(partitionListWidget)

        QMetaObject.connectSlotsByName(partitionListWidget)
    # setupUi

    def retranslateUi(self, partitionListWidget):
        partitionListWidget.setWindowTitle(QCoreApplication.translate("partitionListWidget", u"Erase partition(s)", None))
        self.SelectAllCheckbox.setText(QCoreApplication.translate("partitionListWidget", u"Select all", None))
        self.fullProgressText.setText("")
        self.title.setText(QCoreApplication.translate("partitionListWidget", u"Select partitions to erase", None))
        self.partProgressText.setText(QCoreApplication.translate("partitionListWidget", u"Ready to start...", None))
        self.startBtn.setText(QCoreApplication.translate("partitionListWidget", u"Start", None))
        self.closeBtn.setText(QCoreApplication.translate("partitionListWidget", u"Close", None))
    # retranslateUi

