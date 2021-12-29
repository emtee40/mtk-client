# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_gui.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.NonModal)
        MainWindow.resize(746, 602)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(746, 400))
        MainWindow.setAcceptDrops(False)
        MainWindow.setAutoFillBackground(False)
        self.actionRead_partition_s = QAction(MainWindow)
        self.actionRead_partition_s.setObjectName(u"actionRead_partition_s")
        self.actionRead_full_flash = QAction(MainWindow)
        self.actionRead_full_flash.setObjectName(u"actionRead_full_flash")
        self.actionRead_offset = QAction(MainWindow)
        self.actionRead_offset.setObjectName(u"actionRead_offset")
        self.actionWrite_partition_s = QAction(MainWindow)
        self.actionWrite_partition_s.setObjectName(u"actionWrite_partition_s")
        self.actionWrite_full_flash = QAction(MainWindow)
        self.actionWrite_full_flash.setObjectName(u"actionWrite_full_flash")
        self.actionWrite_at_offset = QAction(MainWindow)
        self.actionWrite_at_offset.setObjectName(u"actionWrite_at_offset")
        self.actionErase_partitions_s = QAction(MainWindow)
        self.actionErase_partitions_s.setObjectName(u"actionErase_partitions_s")
        self.actionErase_at_offset = QAction(MainWindow)
        self.actionErase_at_offset.setObjectName(u"actionErase_at_offset")
        self.actionRead_RPMB = QAction(MainWindow)
        self.actionRead_RPMB.setObjectName(u"actionRead_RPMB")
        self.actionWrite_RPMB = QAction(MainWindow)
        self.actionWrite_RPMB.setObjectName(u"actionWrite_RPMB")
        self.actionRead_preloader = QAction(MainWindow)
        self.actionRead_preloader.setObjectName(u"actionRead_preloader")
        self.actionGenerate_RPMB_keys = QAction(MainWindow)
        self.actionGenerate_RPMB_keys.setObjectName(u"actionGenerate_RPMB_keys")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.widget_3 = QWidget(self.centralwidget)
        self.widget_3.setObjectName(u"widget_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widget_3.sizePolicy().hasHeightForWidth())
        self.widget_3.setSizePolicy(sizePolicy1)
        self.widget_3.setMinimumSize(QSize(70, 128))
        self.pic = QLabel(self.widget_3)
        self.pic.setObjectName(u"pic")
        self.pic.setGeometry(QRect(0, 0, 71, 128))
        sizePolicy2 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pic.sizePolicy().hasHeightForWidth())
        self.pic.setSizePolicy(sizePolicy2)
        self.pic.setMinimumSize(QSize(50, 128))
        self.pic.setMaximumSize(QSize(87, 128))
        self.pic.setPixmap(QPixmap(u"images/phone_notfound.png"))
        self.pic.setScaledContents(True)
        self.pic.setAlignment(Qt.AlignCenter)
        self.pic.setWordWrap(False)
        self.spinner_pic = QLabel(self.widget_3)
        self.spinner_pic.setObjectName(u"spinner_pic")
        self.spinner_pic.setGeometry(QRect(10, 40, 51, 51))
        sizePolicy1.setHeightForWidth(self.spinner_pic.sizePolicy().hasHeightForWidth())
        self.spinner_pic.setSizePolicy(sizePolicy1)
        self.spinner_pic.setPixmap(QPixmap(u"images/phone_loading.png"))
        self.spinner_pic.setScaledContents(True)
        self.spinner_pic.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.widget_3, 0, 2, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.title = QLabel(self.centralwidget)
        self.title.setObjectName(u"title")
        self.title.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.title.sizePolicy().hasHeightForWidth())
        self.title.setSizePolicy(sizePolicy1)
        self.title.setMinimumSize(QSize(0, 24))
        self.title.setMaximumSize(QSize(16777215, 20))
        font = QFont()
        font.setFamily(u"Arial")
        font.setPointSize(18)
        self.title.setFont(font)
        self.title.setLineWidth(0)
        self.title.setTextFormat(Qt.AutoText)
        self.title.setScaledContents(False)
        self.title.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.title.setWordWrap(False)
        self.title.setIndent(0)

        self.verticalLayout.addWidget(self.title)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.logoPic = QLabel(self.centralwidget)
        self.logoPic.setObjectName(u"logoPic")
        sizePolicy1.setHeightForWidth(self.logoPic.sizePolicy().hasHeightForWidth())
        self.logoPic.setSizePolicy(sizePolicy1)
        self.logoPic.setMinimumSize(QSize(128, 128))
        self.logoPic.setMaximumSize(QSize(128, 128))
        self.logoPic.setPixmap(QPixmap(u"images/logo_256.png"))
        self.logoPic.setScaledContents(True)
        self.logoPic.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.horizontalLayout.addWidget(self.logoPic)

        self.copyrightInfo = QLabel(self.centralwidget)
        self.copyrightInfo.setObjectName(u"copyrightInfo")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.copyrightInfo.sizePolicy().hasHeightForWidth())
        self.copyrightInfo.setSizePolicy(sizePolicy3)

        self.horizontalLayout.addWidget(self.copyrightInfo)

        self.phoneInfoTextbox = QLabel(self.centralwidget)
        self.phoneInfoTextbox.setObjectName(u"phoneInfoTextbox")
        sizePolicy3.setHeightForWidth(self.phoneInfoTextbox.sizePolicy().hasHeightForWidth())
        self.phoneInfoTextbox.setSizePolicy(sizePolicy3)
        self.phoneInfoTextbox.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)
        self.phoneInfoTextbox.setWordWrap(True)

        self.horizontalLayout.addWidget(self.phoneInfoTextbox)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.gridLayout_2.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line_2, 1, 0, 1, 4)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_2.addWidget(self.line, 3, 0, 1, 4)

        self.status = QLabel(self.centralwidget)
        self.status.setObjectName(u"status")
        sizePolicy2.setHeightForWidth(self.status.sizePolicy().hasHeightForWidth())
        self.status.setSizePolicy(sizePolicy2)
        self.status.setMinimumSize(QSize(400, 0))
        self.status.setTextFormat(Qt.AutoText)
        self.status.setScaledContents(False)
        self.status.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.status.setWordWrap(False)

        self.gridLayout_2.addWidget(self.status, 2, 0, 1, 2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")

        self.gridLayout.addWidget(self.widget_2, 2, 0, 1, 1)

        self.debugBtn = QPushButton(self.centralwidget)
        self.debugBtn.setObjectName(u"debugBtn")
        sizePolicy1.setHeightForWidth(self.debugBtn.sizePolicy().hasHeightForWidth())
        self.debugBtn.setSizePolicy(sizePolicy1)
        self.debugBtn.setMinimumSize(QSize(110, 0))
        self.debugBtn.setAutoDefault(False)
        self.debugBtn.setFlat(False)

        self.gridLayout.addWidget(self.debugBtn, 0, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 0, 1, 1)

        self.logBox = QPlainTextEdit(self.centralwidget)
        self.logBox.setObjectName(u"logBox")
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.logBox.sizePolicy().hasHeightForWidth())
        self.logBox.setSizePolicy(sizePolicy4)
        self.logBox.setMinimumSize(QSize(722, 0))
        self.logBox.setStyleSheet(u"")
        self.logBox.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.logBox.setReadOnly(True)
        self.logBox.setProperty("hidden", False)

        self.gridLayout.addWidget(self.logBox, 1, 0, 1, 2)


        self.gridLayout_2.addLayout(self.gridLayout, 4, 0, 1, 4)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 746, 22))
        self.readFlashMenu = QMenu(self.menubar)
        self.readFlashMenu.setObjectName(u"readFlashMenu")
        self.writeFlashMenu = QMenu(self.menubar)
        self.writeFlashMenu.setObjectName(u"writeFlashMenu")
        self.eraseFlashMenu = QMenu(self.menubar)
        self.eraseFlashMenu.setObjectName(u"eraseFlashMenu")
        self.toolsFlashMenu = QMenu(self.menubar)
        self.toolsFlashMenu.setObjectName(u"toolsFlashMenu")
        MainWindow.setMenuBar(self.menubar)

        self.menubar.addAction(self.readFlashMenu.menuAction())
        self.menubar.addAction(self.writeFlashMenu.menuAction())
        self.menubar.addAction(self.eraseFlashMenu.menuAction())
        self.menubar.addAction(self.toolsFlashMenu.menuAction())
        self.readFlashMenu.addAction(self.actionRead_partition_s)
        self.readFlashMenu.addAction(self.actionRead_full_flash)
        self.writeFlashMenu.addAction(self.actionWrite_partition_s)
        self.writeFlashMenu.addAction(self.actionWrite_full_flash)
        self.writeFlashMenu.addAction(self.actionWrite_at_offset)
        self.eraseFlashMenu.addAction(self.actionErase_partitions_s)
        self.eraseFlashMenu.addAction(self.actionErase_at_offset)
        self.toolsFlashMenu.addAction(self.actionRead_RPMB)
        self.toolsFlashMenu.addAction(self.actionWrite_RPMB)
        self.toolsFlashMenu.addAction(self.actionRead_preloader)
        self.toolsFlashMenu.addSeparator()
        self.toolsFlashMenu.addAction(self.actionGenerate_RPMB_keys)

        self.retranslateUi(MainWindow)

        self.debugBtn.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MTKClient v2.0", None))
        self.actionRead_partition_s.setText(QCoreApplication.translate("MainWindow", u"Read partition(s)", None))
        self.actionRead_full_flash.setText(QCoreApplication.translate("MainWindow", u"Read full flash", None))
        self.actionRead_offset.setText(QCoreApplication.translate("MainWindow", u"Read at offset", None))
        self.actionWrite_partition_s.setText(QCoreApplication.translate("MainWindow", u"Write partition(s)", None))
        self.actionWrite_full_flash.setText(QCoreApplication.translate("MainWindow", u"Write full flash", None))
        self.actionWrite_at_offset.setText(QCoreApplication.translate("MainWindow", u"Write at offset", None))
        self.actionErase_partitions_s.setText(QCoreApplication.translate("MainWindow", u"Erase partitions(s)", None))
        self.actionErase_at_offset.setText(QCoreApplication.translate("MainWindow", u"Erase at offset", None))
        self.actionRead_RPMB.setText(QCoreApplication.translate("MainWindow", u"Read RPMB", None))
        self.actionWrite_RPMB.setText(QCoreApplication.translate("MainWindow", u"Write RPMB", None))
        self.actionRead_preloader.setText(QCoreApplication.translate("MainWindow", u"Read preloader", None))
        self.actionGenerate_RPMB_keys.setText(QCoreApplication.translate("MainWindow", u"Generate RPMB keys", None))
        self.pic.setText("")
        self.spinner_pic.setText("")
        self.title.setText(QCoreApplication.translate("MainWindow", u"MTKClient v2.0", None))
        self.logoPic.setText("")
        self.copyrightInfo.setText(QCoreApplication.translate("MainWindow", u"<b>Made by:</b> Bjoern Kerler<br/><b>Gui by:</b> Geert-Jan Kreileman<br/><br/><b>Credits:</b><br/>kamakiri [xyzz]<br/>linecode exploit [chimera]<br/>Chaosmaster<br/>and all contributers</p>", None))
        self.phoneInfoTextbox.setText(QCoreApplication.translate("MainWindow", u"No phone detected.", None))
        self.status.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Please connect a Mediatek phone to continue.<br/><br/><span style=\" font-weight:600;\">Hint:</span> Power off the phone before connecting.<br/><span style=\" font-style:italic; color:#393939;\">For brom mode:</span><span style=\" color:#393939;\"><br/>Press and hold vol up, vol dwn, or all hw buttons and connect usb.<br/></span><span style=\" font-style:italic; color:#393939;\">For preloader mode:</span><span style=\" color:#393939;\"><br/>Don't press any hw button and connect usb.</span></p></body></html>", None))
        self.debugBtn.setText(QCoreApplication.translate("MainWindow", u"Show debug log", None))
        self.readFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Read Flash", None))
        self.writeFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Write Flash", None))
        self.eraseFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Erase Flash", None))
        self.toolsFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Tools", None))
    # retranslateUi

