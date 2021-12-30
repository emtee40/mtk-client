import math
from random import random

from PySide2.QtCore import Slot, QCoreApplication
from PySide2.QtWidgets import QDialog, QFileDialog
import mock
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread
from mtkclient.gui.readfull_gui import Ui_readWidget
import os
import sys
import time

sys.excepthook = trap_exc_during_debug


class FDialog():
    lastpath = "."

    def __init__(self, parent):
        self.parent = parent

    def save(self, filename=""):
        fname = os.path.join(self.lastpath, filename)
        ret = QFileDialog.getSaveFileName(parent=self.parent, caption=self.parent.tr("Select output file"), dir=fname,
                                          filter="Binary dump (*.bin)")
        if ret:
            fname = ret[0]
            if fname != "":
                self.lastpath = os.path.dirname(fname)
                return fname
        return None


class ReadFullFlashWindow(QDialog):
    # Partition
    @Slot()
    def updateDumpState(self):
        totalBytes = self.dumpStatus["totalBytes"]
        doneBytes = self.dumpStatus["doneBytes"]
        fullPercentageDone = round((doneBytes / totalBytes) * 100)
        self.ui.progress.setValue(fullPercentageDone)
        self.ui.progressText.setText("Total: (" + str(round((doneBytes / 1024 / 1024))) + "Mb / " + str(
            round((totalBytes / 1024 / 1024))) + " Mb)")

    def updateDumpStateAsync(self, toolkit, parameters):
        while not self.dumpStatus["done"]:
            time.sleep(0.1)
            try:
                self.dumpStatus["totalBytes"] = self.flashsize
                self.dumpStatus["doneBytes"] = os.stat(self.dumpStatus["dumpFile"]).st_size
                toolkit.sendUpdateSignal.emit()
            except:
                time.sleep(0.1)
        self.ui.startBtn.setEnabled(True)

    def dumpPartDone(self):
        self.sendToLogSignal.emit("dump done!")

    def dumpFlash(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("flash.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self, n=0, function=self.dumpFlashAsync, parameters=["user"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpRpmb(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("rpmb.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self, n=0, function=self.dumpFlashAsync, parameters=["rpmb"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpBoot2(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("boot2.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self, n=0, function=self.dumpFlashAsync, parameters=["boot2"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpBoot1(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = self.fdialog.save("boot1.bin")
        if self.dumpFile:
            thread = asyncThread(parent=self, n=0, function=self.dumpFlashAsync, parameters=["boot1"])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.start()
        else:
            self.ui.startBtn.setEnabled(True)

    def dumpFlashAsync(self, toolkit, parameters):
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
            self.mtkClass.daloader.read_rpmb(variables.filename)
        else:
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

    def convert_size(self, size_bytes):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])

    def __init__(self, parent, mtkClass, da_handler, sendToLog,
                 parttype: str = "user"):  # def __init__(self, *args, **kwargs):
        super(ReadFullFlashWindow, self).__init__(parent)
        self.fdialog = FDialog(self)
        self.mtkClass = mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.dumpStatus = {}
        self.da_handler = da_handler
        # self.setFixedSize(400, 500)

        # partitionListWidget = QWidget(self)
        self.ui = Ui_readWidget()
        self.ui.setupUi(self)
        if parttype != "user":
            self.ui.DumpGPTCheckbox.setHidden(True)
            # self.setWindowTitle(self.translate("readWidget", u"Read rpmb", None))

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
        self.ui.progressText.setText("Ready to dump " + self.convert_size(self.flashsize))
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
