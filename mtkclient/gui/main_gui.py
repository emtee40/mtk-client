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
        MainWindow.resize(689, 648)
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
        self.actionGenerate_RPMB_Keys = QAction(MainWindow)
        self.actionGenerate_RPMB_Keys.setObjectName(u"actionGenerate_RPMB_Keys")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.formLayout = QFormLayout(self.centralwidget)
        self.formLayout.setObjectName(u"formLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.title = QLabel(self.centralwidget)
        self.title.setObjectName(u"title")
        font = QFont()
        font.setPointSize(17)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)

        self.verticalLayout_2.addWidget(self.title)

        self.status = QLabel(self.centralwidget)
        self.status.setObjectName(u"status")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status.sizePolicy().hasHeightForWidth())
        self.status.setSizePolicy(sizePolicy)

        self.verticalLayout_2.addWidget(self.status)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy1)
        self.frame.setMinimumSize(QSize(100, 128))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Sunken)
        self.pic = QLabel(self.frame)
        self.pic.setObjectName(u"pic")
        self.pic.setGeometry(QRect(0, 0, 90, 128))
        sizePolicy.setHeightForWidth(self.pic.sizePolicy().hasHeightForWidth())
        self.pic.setSizePolicy(sizePolicy)
        self.pic.setMaximumSize(QSize(16777215, 16777215))
        self.pic.setPixmap(QPixmap(u"images/phone_notfound.png"))
        self.pic.setScaledContents(True)
        self.pic.setAlignment(Qt.AlignCenter)
        self.pic.setWordWrap(False)
        self.spinner_pic = QLabel(self.frame)
        self.spinner_pic.setObjectName(u"spinner_pic")
        self.spinner_pic.setGeometry(QRect(25, 40, 41, 41))
        self.spinner_pic.setPixmap(QPixmap(u"images/phone_loading.png"))
        self.spinner_pic.setScaledContents(True)

        self.horizontalLayout.addWidget(self.frame)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.phoneInfoTextbox = QLabel(self.centralwidget)
        self.phoneInfoTextbox.setObjectName(u"phoneInfoTextbox")
        sizePolicy.setHeightForWidth(self.phoneInfoTextbox.sizePolicy().hasHeightForWidth())
        self.phoneInfoTextbox.setSizePolicy(sizePolicy)
        self.phoneInfoTextbox.setAlignment(Qt.AlignRight|Qt.AlignTop|Qt.AlignTrailing)
        self.phoneInfoTextbox.setWordWrap(True)

        self.verticalLayout.addWidget(self.phoneInfoTextbox)


        self.horizontalLayout_3.addLayout(self.verticalLayout)


        self.formLayout.setLayout(0, QFormLayout.SpanningRole, self.horizontalLayout_3)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.formLayout.setWidget(1, QFormLayout.SpanningRole, self.line)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.logoPic = QLabel(self.centralwidget)
        self.logoPic.setObjectName(u"logoPic")
        sizePolicy1.setHeightForWidth(self.logoPic.sizePolicy().hasHeightForWidth())
        self.logoPic.setSizePolicy(sizePolicy1)
        self.logoPic.setMaximumSize(QSize(100, 100))
        self.logoPic.setPixmap(QPixmap(u"images/logo_256.png"))
        self.logoPic.setScaledContents(True)
        self.logoPic.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)

        self.horizontalLayout_2.addWidget(self.logoPic)

        self.copyrightInfo = QLabel(self.centralwidget)
        self.copyrightInfo.setObjectName(u"copyrightInfo")

        self.horizontalLayout_2.addWidget(self.copyrightInfo)


        self.formLayout.setLayout(3, QFormLayout.LabelRole, self.horizontalLayout_2)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.debugBtn = QPushButton(self.centralwidget)
        self.debugBtn.setObjectName(u"debugBtn")
        sizePolicy2 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.debugBtn.sizePolicy().hasHeightForWidth())
        self.debugBtn.setSizePolicy(sizePolicy2)

        self.verticalLayout_3.addWidget(self.debugBtn)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)


        self.horizontalLayout_4.addLayout(self.verticalLayout_3)


        self.formLayout.setLayout(3, QFormLayout.FieldRole, self.horizontalLayout_4)

        self.logBox = QPlainTextEdit(self.centralwidget)
        self.logBox.setObjectName(u"logBox")
        self.logBox.setReadOnly(True)

        self.formLayout.setWidget(2, QFormLayout.SpanningRole, self.logBox)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 689, 22))
        self.readFlashMenu = QMenu(self.menubar)
        self.readFlashMenu.setObjectName(u"readFlashMenu")
        self.writeFlashMenu = QMenu(self.menubar)
        self.writeFlashMenu.setObjectName(u"writeFlashMenu")
        self.eraseFlashMenu = QMenu(self.menubar)
        self.eraseFlashMenu.setObjectName(u"eraseFlashMenu")
        self.toolsFlashMenu = QMenu(self.menubar)
        self.toolsFlashMenu.setObjectName(u"toolsFlashMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.readFlashMenu.menuAction())
        self.menubar.addAction(self.writeFlashMenu.menuAction())
        self.menubar.addAction(self.eraseFlashMenu.menuAction())
        self.menubar.addAction(self.toolsFlashMenu.menuAction())
        self.readFlashMenu.addAction(self.actionRead_partition_s)
        self.readFlashMenu.addAction(self.actionRead_full_flash)
        self.readFlashMenu.addAction(self.actionRead_offset)
        self.writeFlashMenu.addAction(self.actionWrite_partition_s)
        self.writeFlashMenu.addAction(self.actionWrite_full_flash)
        self.writeFlashMenu.addAction(self.actionWrite_at_offset)
        self.eraseFlashMenu.addAction(self.actionErase_partitions_s)
        self.eraseFlashMenu.addAction(self.actionErase_at_offset)
        self.toolsFlashMenu.addAction(self.actionRead_RPMB)
        self.toolsFlashMenu.addAction(self.actionWrite_RPMB)
        self.toolsFlashMenu.addAction(self.actionRead_preloader)
        self.toolsFlashMenu.addSeparator()
        self.toolsFlashMenu.addAction(self.actionGenerate_RPMB_Keys)

        self.retranslateUi(MainWindow)

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
        self.actionGenerate_RPMB_Keys.setText(QCoreApplication.translate("MainWindow", u"Generate RPMB Keys", None))
        self.title.setText(QCoreApplication.translate("MainWindow", u"MTKClient v2.0", None))
        self.status.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Please connect a Mediatek phone to continue.</p><p><br/></p><p>Hint: Power off the phone before connecting.</p><p><br/></p><p>For brom mode:</p><p>Press and hold vol up, vol dwn, or all hw buttons and connect usb.</p><p><br/></p><p>For preloader mode:</p><p>Don't press any hw button and connect usb.</p></body></html>", None))
        self.pic.setText("")
        self.spinner_pic.setText("")
        self.phoneInfoTextbox.setText(QCoreApplication.translate("MainWindow", u"No phone detected.", None))
        self.logoPic.setText("")
        self.copyrightInfo.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt;\">Made by: 	Bjoern Kerler<br/>Gui by: 	Geert-Jan Kreileman<br/></span></p><p><span style=\" font-size:12pt;\">Credits:<br/>	kamakiri [xyzz]<br/>	linecode exploit [chimera]<br/>	Chaosmaster<br/>	and all contributers</span></p></body></html>", None))
        self.debugBtn.setText(QCoreApplication.translate("MainWindow", u"Show debug log", None))
        self.readFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Read Flash", None))
        self.writeFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Write Flash", None))
        self.eraseFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Erase Flash", None))
        self.toolsFlashMenu.setTitle(QCoreApplication.translate("MainWindow", u"&Tools", None))
    # retranslateUi

