import math
from random import random

from PySide2.QtCore import Slot, QCoreApplication
from PySide2.QtWidgets import QDialog, QFileDialog
import mock
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread, convert_size, FDialog
from mtkclient.gui.writefull_gui import Ui_writeWidget
import os
import sys
import time

sys.excepthook = trap_exc_during_debug

class WriteFullFlashWindow(QDialog):
    # Partition
    @Slot()
    def updateWriteState(self):
        totalBytes = self.writeStatus["totalBytes"]
        doneBytes = self.writeStatus["doneBytes"]
        fullPercentageDone = round((doneBytes / totalBytes) * 100)
        self.ui.progress.setValue(fullPercentageDone)
        self.ui.progressText.setText("Total: (" + str(round((doneBytes / 1024 / 1024))) + "Mb / " + str(
            round((totalBytes / 1024 / 1024))) + " Mb)")

    @Slot(int)
    def updateProgress(self, progress):
        self.dumpStatus["doneBytes"] = progress
        self.updateDumpState()

    def updateWriteStateAsync(self, toolkit, parameters):
        while not self.writeStatus["done"]:
            time.sleep(0.1)
        self.ui.startBtn.setEnabled(True)

    def writePartDone(self):
        self.sendToLogSignal.emit("write done!")

    def writeFlash(self):
        self.ui.startBtn.setEnabled(False)
        self.writeFile = self.fdialog.open("flash.bin")
        if self.writeFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.writeFlashAsync, parameters=["user"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateWriteState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def writeRpmb(self):
        self.ui.startBtn.setEnabled(False)
        self.writeFile = self.fdialog.open("rpmb.bin")
        if self.writeFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.writeFlashAsync, parameters=["rpmb"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updatewriteState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def writeBoot2(self):
        self.ui.startBtn.setEnabled(False)
        self.writeFile = self.fdialog.open("boot2.bin")
        if self.writeFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.writeFlashAsync, parameters=["boot2"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateWriteState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def writeBoot1(self):
        self.ui.startBtn.setEnabled(False)
        self.writeFile = self.fdialog.open("boot1.bin")
        if self.writeFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.writeFlashAsync, parameters=["boot1"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateWriteState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def writeFlashAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.writeStatus["done"] = False
        thread = asyncThread(self, 0, self.updateWriteStateAsync, [])
        thread.sendUpdateSignal.connect(self.updateWriteState)
        thread.start()
        variables = mock.Mock()
        variables.filename = self.writeFile
        variables.parttype = None
        self.writeStatus["writeFile"] = variables.filename
        self.da_handler.close = self.writePartDone  # Ignore the normally used sys.exit
        if "rpmb" in parameters:
            self.mtkClass.daloader.read_rpmb(variables.filename)
        else:
            if "boot1" in parameters:
                variables.parttype = "boot1"
            elif "boot2" in parameters:
                variables.parttype = "boot2"
            else:
                variables.parttype = "user"
            self.da_handler.handle_da_cmds(self.mtkClass, "wf", variables)
        self.writeStatus["done"] = True
        thread.wait()

    def __init__(self, parent, devhandler, da_handler, sendToLog,
                 parttype: str = "user"):  # def __init__(self, *args, **kwargs):
        super(WriteFullFlashWindow, self).__init__(parent)
        self.fdialog = FDialog(self)
        devhandler.sendToProgressSignal.connect(self.updateProgress)
        self.mtkClass = devhandler.mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.writeStatus = {}
        self.da_handler = da_handler
        # self.setFixedSize(400, 500)

        # partitionListWidget = QWidget(self)
        self.ui = Ui_writeWidget()
        self.ui.setupUi(self)
        self.flashsize = 0
        if parttype == "user":
            self.flashsize = self.mtkClass.daloader.daconfig.flashsize
            self.ui.startBtn.clicked.connect(self.writeFlash)
            self.setWindowTitle(QCoreApplication.translate("writeWidget", u"Write full flash", None))
        elif parttype == "rpmb":
            self.flashsize = self.mtkClass.daloader.daconfig.rpmbsize
            self.ui.startBtn.clicked.connect(self.writeRpmb)
            self.setWindowTitle(QCoreApplication.translate("writeWidget", u"Write rpmb", None))
        elif parttype == "boot1":
            self.flashsize = self.mtkClass.daloader.daconfig.boot1size
            self.ui.startBtn.clicked.connect(self.writeBoot1)
            self.setWindowTitle(QCoreApplication.translate("writeWidget", u"Write preloader", None))
        elif parttype == "boot2":
            self.flashsize = self.mtkClass.daloader.daconfig.boot2size
            self.ui.startBtn.clicked.connect(self.writeBoot2)
            self.setWindowTitle(QCoreApplication.translate("writeWidget", u"Write boot2", None))
        self.ui.progressText.setText(self.tr("Ready to write ") + convert_size(self.flashsize))
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
