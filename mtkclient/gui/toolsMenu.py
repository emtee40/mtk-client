from random import random

from PySide6.QtCore import Slot, Qt, QSize, QRect
from PySide6.QtGui import QTextOption, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QDialog
import mock
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread, FDialog
from mtkclient.Library.mtk import Mtk
from mtkclient.Library.mtk_da_cmd import DA_handler
import os
import sys
import time

sys.excepthook = trap_exc_during_debug


class generateKeysMenu(QDialog):
    # Partition
    @Slot(int)
    def updateProgress(self, progress):
        return

    @Slot()
    def updateKeys(self):
        print(self.keysStatus)
        path = os.path.join(self.hwparamFolder, "hwparam.json")
        self.statusText.setText(f"Keys saved to {path}.")
        # self.keyListText.setText("RPMB key: ")
        retkey = ""
        retlist = ""
        for keys in self.keysStatus['result']:
            skey = self.keysStatus['result'][keys]
            if skey is not None:
                retlist += keys + ":\n"
                retkey += skey + "\n"
        self.keyListText.setText(retlist)
        self.keyListText.setStyleSheet("font-weight: bold")
        self.keyValueText.setText(retkey)
        self.sendToLogSignal.emit("Keys generated!")

    def generateKeys(self):
        self.startBtn.setEnabled(False)
        self.statusText.setText("Generating...")
        hwparamFolder = self.fdialog.opendir(self.tr("Select output directory"))
        if hwparamFolder == "":
            hwparamFolder = "logs"
        else:
            self.mtkClass.config.set_hwparam_path(hwparamFolder)
        self.hwparamFolder = hwparamFolder
        thread = asyncThread(self, 0, self.generateKeysAsync, [self.hwparamFolder])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateKeys)
        thread.start()

    def generateKeysAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.sendUpdateSignal = toolkit.sendUpdateSignal
        toolkit.sendToLogSignal.emit("Generating keys")
        self.keysStatus["result"] = self.mtkClass.daloader.keys()
        # MtkTool.cmd_stage(mtkClass, None, None, None, False)
        self.keysStatus["done"] = True
        self.sendUpdateSignal.emit()

    def __init__(self, parent, devhandler, da_handler: DA_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(generateKeysMenu, self).__init__(parent)
        self.parent = parent
        self.fdialog = FDialog(self)
        devhandler.sendToProgressSignal.connect(self.updateProgress)
        self.mtkClass = devhandler.mtkClass
        self.sendToLog = sendToLog
        self.keysStatus = {}
        self.da_handler = da_handler
        self.setFixedSize(700, 170)
        # widget = QWidget()
        self.setWindowTitle("Generate RPMB Keys")

        title = QLabel(self)
        title.setGeometry(10, 0, 150, 40)
        title.setText("Generate RPMB Keys")

        # Line
        line = QFrame(self)
        line.setGeometry(10, 25, 680, 20)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        # Info
        self.keyListText = QLabel(self)
        self.keyListText.setText("")
        self.keyListText.setStyleSheet("font-weight: bold")
        self.keyListText.setGeometry(10, 30, 380, 90)

        self.keyValueText = QLabel(self)
        self.keyValueText.setText("")
        self.keyValueText.setGeometry(100, 30, 580, 90)

        # Status text
        self.statusText = QLabel(self)
        self.statusText.setText("Ready to start.")
        self.statusText.setStyleSheet("font-style: italic color:#555")
        self.statusText.setGeometry(10, 135, (580 - 150), 20)

        # start button
        self.startBtn = QPushButton(self)
        self.startBtn.setText("Generate keys")
        self.startBtn.clicked.connect(self.generateKeys)
        self.startBtn.setGeometry((700 - 150 - 110), (170 - 30 - 10), 150, 30)
        self.startBtn.show()

        self.closeBtn = QPushButton(self)
        self.closeBtn.setText("Close")
        self.closeBtn.clicked.connect(self.close)
        self.closeBtn.setGeometry((700 - 80 - 10), (170 - 30 - 10), 80, 30)
        self.closeBtn.show()

        self.show()
        # parent.setCentralWidget(self)
