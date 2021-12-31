# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'writefull_gui.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_writeWidget(object):
    def setupUi(self, writeWidget):
        if not writeWidget.objectName():
            writeWidget.setObjectName(u"writeWidget")
        writeWidget.resize(402, 168)
        self.gridLayout_2 = QGridLayout(writeWidget)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(-1, 9, -1, 8)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetNoConstraint)
        self.startBtn = QPushButton(writeWidget)
        self.startBtn.setObjectName(u"startBtn")

        self.horizontalLayout.addWidget(self.startBtn)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.closeBtn = QPushButton(writeWidget)
        self.closeBtn.setObjectName(u"closeBtn")

        self.horizontalLayout.addWidget(self.closeBtn)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.progressText = QLabel(writeWidget)
        self.progressText.setObjectName(u"progressText")

        self.verticalLayout.addWidget(self.progressText)

        self.progress = QProgressBar(writeWidget)
        self.progress.setObjectName(u"progress")
        self.progress.setMaximumSize(QSize(16777215, 100))
        self.progress.setValue(0)

        self.verticalLayout.addWidget(self.progress)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)


        self.retranslateUi(writeWidget)

        QMetaObject.connectSlotsByName(writeWidget)
    # setupUi

    def retranslateUi(self, writeWidget):
        writeWidget.setWindowTitle(QCoreApplication.translate("writeWidget", u"Write full flash", None))
        self.startBtn.setText(QCoreApplication.translate("writeWidget", u"Start", None))
        self.closeBtn.setText(QCoreApplication.translate("writeWidget", u"Close", None))
        self.progressText.setText(QCoreApplication.translate("writeWidget", u"Ready to start...", None))
    # retranslateUi

