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
        MainWindow.resize(746, 574)
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
        self.spinner_pic = QLabel(self.centralwidget)
        self.spinner_pic.setObjectName(u"spinner_pic")
        self.spinner_pic.setGeometry(QRect(655, 42, 64, 64))
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinner_pic.sizePolicy().hasHeightForWidth())
        self.spinner_pic.setSizePolicy(sizePolicy1)
        self.spinner_pic.setPixmap(QPixmap(u"images/phone_loading.png"))
        self.spinner_pic.setScaledContents(False)
        self.spinner_pic.setAlignment(Qt.AlignCenter)
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
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

        self.gridLayout.addWidget(self.title, 0, 0, 1, 1)

        self.pic = QLabel(self.centralwidget)
        self.pic.setObjectName(u"pic")
        sizePolicy1.setHeightForWidth(self.pic.sizePolicy().hasHeightForWidth())
        self.pic.setSizePolicy(sizePolicy1)
        self.pic.setMinimumSize(QSize(60, 128))
        self.pic.setMaximumSize(QSize(87, 128))
        self.pic.setPixmap(QPixmap(u"images/phone_notfound.png"))
        self.pic.setScaledContents(True)
        self.pic.setAlignment(Qt.AlignCenter)
        self.pic.setWordWrap(False)

        self.gridLayout.addWidget(self.pic, 0, 3, 2, 1)

        self.phoneInfoTextbox = QLabel(self.centralwidget)
        self.phoneInfoTextbox.setObjectName(u"phoneInfoTextbox")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.phoneInfoTextbox.sizePolicy().hasHeightForWidth())
        self.phoneInfoTextbox.setSizePolicy(sizePolicy2)
        self.phoneInfoTextbox.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)
        self.phoneInfoTextbox.setWordWrap(True)

        self.gridLayout.addWidget(self.phoneInfoTextbox, 0, 2, 1, 1)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 2, 0, 1, 4)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.logoPic = QLabel(self.centralwidget)
        self.logoPic.setObjectName(u"logoPic")
        sizePolicy1.setHeightForWidth(self.logoPic.sizePolicy().hasHeightForWidth())
        self.logoPic.setSizePolicy(sizePolicy1)
        self.logoPic.setMinimumSize(QSize(128, 128))
        self.logoPic.setMaximumSize(QSize(128, 128))
        self.logoPic.setPixmap(QPixmap(u"images/logo_256.png"))
        self.logoPic.setScaledContents(True)
        self.logoPic.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.horizontalLayout_2.addWidget(self.logoPic)

        self.copyrightInfo = QLabel(self.centralwidget)
        self.copyrightInfo.setObjectName(u"copyrightInfo")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.copyrightInfo.sizePolicy().hasHeightForWidth())
        self.copyrightInfo.setSizePolicy(sizePolicy3)

        self.horizontalLayout_2.addWidget(self.copyrightInfo)


        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 0, 1, 4)

        self.status = QLabel(self.centralwidget)
        self.status.setObjectName(u"status")
        sizePolicy2.setHeightForWidth(self.status.sizePolicy().hasHeightForWidth())
        self.status.setSizePolicy(sizePolicy2)
        self.status.setMinimumSize(QSize(400, 0))
        self.status.setTextFormat(Qt.AutoText)
        self.status.setScaledContents(False)
        self.status.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.status.setWordWrap(False)

        self.gridLayout.addWidget(self.status, 1, 0, 1, 3)

        self.logBox = QPlainTextEdit(self.centralwidget)
        self.logBox.setObjectName(u"logBox")
        self.logBox.setMinimumSize(QSize(722, 0))
        self.logBox.setStyleSheet(u"")
        self.logBox.setReadOnly(True)
        self.logBox.setProperty("hidden", False)

        self.gridLayout.addWidget(self.logBox, 5, 0, 1, 4)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setSizeConstraint(QLayout.SetNoConstraint)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.debugBtn = QPushButton(self.centralwidget)
        self.debugBtn.setObjectName(u"debugBtn")
        sizePolicy1.setHeightForWidth(self.debugBtn.sizePolicy().hasHeightForWidth())
        self.debugBtn.setSizePolicy(sizePolicy1)
        self.debugBtn.setMinimumSize(QSize(110, 0))
        self.debugBtn.setAutoDefault(False)
        self.debugBtn.setFlat(False)

        self.horizontalLayout_4.addWidget(self.debugBtn)


        self.gridLayout.addLayout(self.horizontalLayout_4, 4, 0, 1, 4)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 1, 1, 1)

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
        self.spinner_pic.setText("")
        self.title.setText(QCoreApplication.translate("MainWindow", u"MTKClient v2.0", None))
        self.pic.setText("")
        self.phoneInfoTextbox.setText(QCoreApplication.translate("MainWindow", u"No phone detected.", None))
        self.logoPic.setText("")
        self.copyrightInfo.setText(QCoreApplication.translate("MainWindow", u"<b>Made by:</b> Bjoern Kerler<br/><b>Gui by:</b> Geert-Jan Kreileman<br/><br/><b>Credits:</b><br/>kamakiri [xyzz]<br/>linecode exploit [chimera]<br/>Chaosmaster<br/>and all contributers</p>", None))
        self.status.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Please connect a Mediatek phone to continue.<br/><br/><span style=\" font-weight:600;\">Hint:</span> Power off the phone before connecting.<br/><span style=\" font-style:italic; color:#393939;\">For brom mode:</span><span style=\" color:#393939;\"><br/>Press and hold vol up, vol dwn, or all hw buttons and connect usb.<br/></span><span style=\" font-style:italic; color:#393939;\">For preloader mode:</span><span style=\" color:#393939;\"><br/>Don't press any hw button and connect usb.</span></p></body></html>", None))
        self.debugBtn.setText(QCoreApplication.translate("MainWindow", u"Show debug log", None))
        self.readFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Read Flash", None))
        self.writeFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Write Flash", None))
        self.eraseFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Erase Flash", None))
        self.toolsFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Tools", None))
    # retranslateUi

