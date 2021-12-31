from random import random

import os
import sys
import mock
import time
from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QWidget
from mtkclient.gui.toolkit import convert_size, FDialog, TimeEstim, trap_exc_during_debug, asyncThread
from mtkclient.gui.readpart_gui import Ui_partitionListWidget


sys.excepthook = trap_exc_during_debug


class ReadFlashWindow(QDialog):
    # Partition
    @Slot()
    def updateDumpState(self):
        totalBytes = 0
        doneBytes = 0
        for partition in self.dumpStatus["allPartitions"]:
            totalBytes = totalBytes + self.dumpStatus["allPartitions"][partition]['size']
            if (self.dumpStatus["allPartitions"][partition]['done'] and partition != self.dumpStatus[
                "currentPartition"]):
                doneBytes = doneBytes + self.dumpStatus["allPartitions"][partition]['size']
        doneBytes = doneBytes + self.dumpStatus["currentPartitionSizeDone"]
        percentageDone = (self.dumpStatus["currentPartitionSizeDone"] / self.dumpStatus["currentPartitionSize"]) * 100
        fullPercentageDone = (doneBytes / totalBytes) * 100
        self.ui.partProgress.setValue(percentageDone)
        timeinfo = self.timeEst.update(doneBytes, totalBytes)
        self.ui.partProgressText.setText("Current partition: " + self.dumpStatus["currentPartition"] + " (" +
                                         convert_size(self.dumpStatus["currentPartitionSizeDone"]) + " / " +
                                         convert_size(self.dumpStatus["currentPartitionSize"])+
                                         timeinfo+self.tr(" left")+")")

        self.ui.fullProgress.setValue(fullPercentageDone)
        timeinfototal = self.timeEstTotal.update(fullPercentageDone, 100)
        self.ui.fullProgressText.setText("Total: (" + convert_size(doneBytes) + " / " + convert_size(totalBytes)+
                                         timeinfototal + self.tr(" left") + ")")

    @Slot(int)
    def updateProgress(self, progress):
        self.dumpStatus["currentPartitionSizeDone"] = progress
        self.updateDumpState()

    def updateDumpStateAsync(self, toolkit, parameters):
        while not self.dumpStatus["done"]:
            # print(self.dumpStatus)
            time.sleep(0.1)
        print("DONE")
        self.ui.startBtn.setEnabled(True)

    def dumpPartDone(self):
        self.sendToLogSignal.emit("dump done!")

    def selectAll(self):
        if self.ui.SelectAllCheckbox.isChecked():
            for partition in self.partitionCheckboxes:
                self.partitionCheckboxes[partition]['box'].setChecked(True)
        else:
            for partition in self.partitionCheckboxes:
                self.partitionCheckboxes[partition]['box'].setChecked(False)


    def dumpPartition(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFolder = self.fdialog.opendir(self.tr("Select output directory"))
        if self.dumpFolder:
            thread = asyncThread(parent=self.parent, n=0, function=self.dumpPartitionAsync,parameters=[])
            thread.sendToLogSignal.connect(self.sendToLog)
            thread.sendUpdateSignal.connect(self.updateDumpState)
            thread.sendToProgressSignal.connect(self.updateProgress)
            thread.start()


    def dumpPartitionAsync(self, toolkit, parameters):
        self.timeEst.init()
        self.timeEstTotal.init()
        self.sendToLogSignal = toolkit.sendToLogSignal
        toolkit.sendToLogSignal.emit("test")
        self.dumpStatus["done"] = False
        thread = asyncThread(self.parent, 0, self.updateDumpStateAsync, [])
        thread.sendUpdateSignal.connect(self.updateDumpState)
        thread.sendToProgressSignal.connect(self.updateProgress)
        thread.start()
        # calculate total bytes
        self.dumpStatus["allPartitions"] = {}
        for partition in self.partitionCheckboxes:
            if self.partitionCheckboxes[partition]['box'].isChecked():
                self.dumpStatus["allPartitions"][partition] = {"size": self.partitionCheckboxes[partition]['size'],
                                                               "done": False}
        for partition in self.partitionCheckboxes:
            if self.partitionCheckboxes[partition]['box'].isChecked():
                variables = mock.Mock()
                variables.partitionname = partition
                variables.filename = os.path.join(self.dumpFolder, partition + ".bin")
                variables.parttype = None
                self.dumpStatus["currentPartitionSize"] = self.partitionCheckboxes[partition]['size']
                self.dumpStatus["currentPartition"] = partition
                self.dumpStatus["currentPartitionFile"] = variables.filename
                self.da_handler.close = self.dumpPartDone  # Ignore the normally used sys.exit
                self.da_handler.handle_da_cmds(self.mtkClass, "r", variables)
                self.dumpStatus["allPartitions"][partition]['done'] = True
                # MtkTool.cmd_stage(mtkClass, None, None, None, False)
        if self.ui.DumpGPTCheckbox.isChecked():
            #also dump the GPT
            variables = mock.Mock()
            variables.directory = self.dumpFolder
            variables.parttype = None
            self.dumpStatus["allPartitions"]["GPT"] = {}
            self.dumpStatus["allPartitions"]["GPT"]['size'] = 17
            self.dumpStatus["currentPartition"] = "GPT"
            self.da_handler.close = self.dumpPartDone  # Ignore the normally used sys.exit
            self.da_handler.handle_da_cmds(self.mtkClass, "gpt", variables)
            self.dumpStatus["allPartitions"]["GPT"]['done'] = True
        self.dumpStatus["done"] = True
        thread.wait()

    def __init__(self, parent, devhandler, da_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(ReadFlashWindow, self).__init__(parent)
        devhandler.sendToProgressSignal.connect(self.updateProgress)
        self.timeEst = TimeEstim()
        self.timeEstTotal = TimeEstim()
        self.mtkClass = devhandler.mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.dumpStatus = {}
        self.fdialog = FDialog(self)
        self.da_handler = da_handler
        #self.setFixedSize(400, 500)
        self.setWindowTitle("Read partition(s)")

        #partitionListWidget = QWidget(self)
        self.ui = Ui_partitionListWidget()
        self.ui.setupUi(self)
        data, guid_gpt = self.mtkClass.daloader.get_gpt()
        if guid_gpt is None:
            print("Error reading gpt")
            self.ui.title.setText(self.tr("Error reading gpt"))
        else:
            self.ui.title.setText(self.tr("Select partitions to dump"))
            # guid_gpt.print()

            partitionListWidgetVBox = QVBoxLayout()
            partitionListWidget = QWidget(self)
            partitionListWidget.setLayout(partitionListWidgetVBox)
            self.ui.partitionList.setWidget(partitionListWidget)
            self.ui.partitionList.setWidgetResizable(True)
            self.ui.partitionList.setGeometry(10,40,380,320)
            self.ui.partitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            self.ui.partitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.partitionCheckboxes = {}
            for partition in guid_gpt.partentries:
                self.partitionCheckboxes[partition.name] = {}
                self.partitionCheckboxes[partition.name]['size'] = (partition.sectors * guid_gpt.sectorsize)
                self.partitionCheckboxes[partition.name]['box'] = QCheckBox()
                self.partitionCheckboxes[partition.name]['box'].setText(partition.name + " (" +
                        convert_size(partition.sectors * guid_gpt.sectorsize)+")")
                partitionListWidgetVBox.addWidget(self.partitionCheckboxes[partition.name]['box'])

        self.ui.startBtn.clicked.connect(self.dumpPartition)
        self.ui.SelectAllCheckbox.clicked.connect(self.selectAll)
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
