import math
from random import random

from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QDialog, QFileDialog, QCheckBox, QVBoxLayout, QSizePolicy, QWidget
import mock
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread
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
        fullPercentageDone = round((doneBytes/totalBytes)*100)
        self.ui.progress.setValue(fullPercentageDone)
        self.ui.progressText.setText("Total: (" + str(round((doneBytes / 1024 / 1024))) + "Mb / " + str(
            round((totalBytes / 1024 / 1024))) + " Mb)")

    def updateDumpStateAsync(self, toolkit, parameters):
        while not self.dumpStatus["done"]:
            # print(self.dumpStatus)
            time.sleep(0.1)
            try:
                self.dumpStatus["totalBytes"] = self.mtkClass.daloader.daconfig.flashsize;
                self.dumpStatus["doneBytes"] = os.stat(self.dumpStatus["dumpFile"]).st_size
                toolkit.sendUpdateSignal.emit()
                # self.partProgressText.setText(str(currentPartitionSize)+"Current pa"+str(random(0,100000))+"rtition: "+self.dumpStatus["currentPartition"])
            except:
                time.sleep(0.1)
        self.ui.startBtn.setEnabled(True)

    def dumpPartDone(self):
        self.sendToLogSignal.emit("dump done!")

    def dumpFlash(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFile = str(QFileDialog.getSaveFileName(self, "Select output file", "", "Binary dump (*.bin)")[0])
        # self.startBtn.setText("In progress..")
        thread = asyncThread(parent=self, n=0, function=self.dumpFlashAsync,parameters=[])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateDumpState)
        thread.start()


    def dumpFlashAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        # partitionname = args.partitionname
        # parttype = args.parttype
        # filename = args.filename
        # print(self.partitionCheckboxes)
        self.dumpStatus["done"] = False
        thread = asyncThread(self, 0, self.updateDumpStateAsync, [])
        thread.sendUpdateSignal.connect(self.updateDumpState)
        thread.start()
        # calculate total bytes
        # for partition in self.partitionCheckboxes:
        #    if self.partitionCheckboxes[partition]['box'].isChecked():
        #        self.dumpStatus["totalSize"] = self.dumpStatus["totalSize"]+self.partitionCheckboxes[partition]['size']
        variables = mock.Mock()
        variables.filename = self.dumpFile
        variables.parttype = None
        self.dumpStatus["dumpFile"] = variables.filename
        self.da_handler.close = self.dumpPartDone  # Ignore the normally used sys.exit
        self.da_handler.handle_da_cmds(self.mtkClass, "rf", variables)
        # MtkTool.cmd_stage(mtkClass, None, None, None, False)
        if self.ui.DumpGPTCheckbox.isChecked():
            #also dump the GPT
            variables = mock.Mock()
            variables.directory = os.path.dirname(self.dumpFile);
            variables.parttype = None
            self.da_handler.close = self.dumpPartDone  # Ignore the normally used sys.exit
            self.da_handler.handle_da_cmds(self.mtkClass, "gpt", variables)
        self.dumpStatus["done"] = True
        thread.wait()

    def __init__(self, parent, mtkClass, da_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(ReadFullFlashWindow, self).__init__(parent)
        self.mtkClass = mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.dumpStatus = {}
        self.da_handler = da_handler
        #self.setFixedSize(400, 500)

        #partitionListWidget = QWidget(self)
        self.ui = Ui_readWidget()
        self.ui.setupUi(self)

        self.ui.progressText.setText("Ready to dump "+str(round((self.mtkClass.daloader.daconfig.flashsize/1024/1024/1024)))+" Gb...");

        self.ui.startBtn.clicked.connect(self.dumpFlash)
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
