import math
from random import random

from PySide2.QtCore import Slot, QCoreApplication
from PySide2.QtWidgets import QDialog
import mock
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread, convert_size, FDialog, TimeEstim
from mtkclient.gui.readfull_gui import Ui_readWidget
import os
import sys
import time

sys.excepthook = trap_exc_during_debug

class ReadFullFlashWindow(QDialog):
    # Partition
    @Slot()
    def updateDumpState(self):
        totalBytes = self.dumpStatus["totalBytes"]
        doneBytes = self.dumpStatus["doneBytes"]
        fullPercentageDone = round((doneBytes / totalBytes) * 100)
        self.ui.progress.setValue(fullPercentageDone)
        timeinfo = self.timeEst.update(doneBytes, totalBytes)
        self.ui.progressText.setText("Total: (" + convert_size(doneBytes) + " / " +
                                     convert_size(totalBytes) + " -> "+timeinfo+self.tr(" left")+")")

    @Slot(int)
    def updateProgress(self, progress):
        self.dumpStatus["doneBytes"] = progress * self.factor
        self.dumpStatus["totalBytes"] = self.flashsize
        self.updateDumpState()

    def updateDumpStateAsync(self, toolkit, parameters):
        while not self.dumpStatus["done"]:
            time.sleep(0.1)
            self.dumpStatus["totalBytes"] = self.flashsize
        self.ui.startBtn.setEnabled(True)

    def dumpPartDone(self):
        self.sendToLogSignal.emit("dump done!")

    def dumpFlash(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("flash.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.dumpFlashAsync, parameters=["user"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpRpmb(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("rpmb.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.dumpFlashAsync, parameters=["rpmb"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpBoot2(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("boot2.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.dumpFlashAsync, parameters=["boot2"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpBoot1(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("boot1.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self.parent, n=0, function=self.dumpFlashAsync, parameters=["boot1"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpFlashAsync(self, toolkit, parameters):
        self.timeEst.init()
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.dumpStatus["done"] = False
        thread = asyncThread(self, 0, self.updateDumpStateAsync, [])
        thread.sendUpdateSignal.connect(self.updateDumpState)
        thread.start()
        variables = mock.Mock()
        variables.filename = self.dumpFile
        variables.parttype = None
        self.dumpStatus["dumpFile"] = variables.filename
        self.da_handler.close = self.dumpPartDone  # Ignore the normally used sys.exit
        if "rpmb" in parameters:
            self.factor = 0x100
            self.mtkClass.daloader.read_rpmb(variables.filename)
        else:
            self.factor = 0x1
            if "boot1" in parameters:
                variables.parttype = "boot1"
            elif "boot2" in parameters:
                variables.parttype = "boot2"
            else:
                variables.parttype = "user"
            self.da_handler.handle_da_cmds(self.mtkClass, "rf", variables)
        if self.ui.DumpGPTCheckbox.isChecked():
            # also dump the GPT
            variables = mock.Mock()
            variables.directory = os.path.dirname(self.dumpFile)
            variables.parttype = None
            self.da_handler.close = self.dumpPartDone  # Ignore the normally used sys.exit
            self.da_handler.handle_da_cmds(self.mtkClass, "gpt", variables)
        self.dumpStatus["done"] = True
        thread.wait()

    def __init__(self, parent, devhandler, da_handler, sendToLog,
                 parttype: str = "user"):  # def __init__(self, *args, **kwargs):
        super(ReadFullFlashWindow, self).__init__(parent)
        self.timeEst = TimeEstim()
        self.fdialog = FDialog(self)
        devhandler.sendToProgressSignal.connect(self.updateProgress)
        self.mtkClass = devhandler.mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.factor = 1
        if parttype=="rpmb":
            self.factor = 0x100
        self.dumpStatus = {}
        self.da_handler = da_handler
        # self.setFixedSize(400, 500)

        # partitionListWidget = QWidget(self)
        self.ui = Ui_readWidget()
        self.ui.setupUi(self)
        if parttype != "user":
            self.ui.DumpGPTCheckbox.setHidden(True)
            self.ui.label_2.setHidden(True)
            # self.setWindowTitle(self.translate("readWidget", u"Read rpmb", None))
        else:
            self.ui.DumpGPTCheckbox.setHidden(False)
            self.ui.label_2.setHidden(False)
        self.flashsize = 0
        if parttype == "user":
            self.flashsize = self.mtkClass.daloader.daconfig.flashsize
            self.ui.startBtn.clicked.connect(self.dumpFlash)
            self.setWindowTitle(QCoreApplication.translate("readWidget", u"Read full flash", None))
        elif parttype == "rpmb":
            self.flashsize = self.mtkClass.daloader.daconfig.rpmbsize
            self.ui.startBtn.clicked.connect(self.dumpRpmb)
            self.setWindowTitle(QCoreApplication.translate("readWidget", u"Read rpmb", None))
        elif parttype == "boot1":
            self.flashsize = self.mtkClass.daloader.daconfig.boot1size
            self.ui.startBtn.clicked.connect(self.dumpBoot1)
            self.setWindowTitle(QCoreApplication.translate("readWidget", u"Read preloader", None))
        elif parttype == "boot2":
            self.flashsize = self.mtkClass.daloader.daconfig.boot2size
            self.ui.startBtn.clicked.connect(self.dumpBoot2)
            self.setWindowTitle(QCoreApplication.translate("readWidget", u"Read boot2", None))
        self.ui.progressText.setText(self.tr("Ready to dump ") + convert_size(self.flashsize))
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
