from random import random

import os
import sys
import mock
import time
from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QWidget
from mtkclient.gui.toolkit import convert_size, FDialog, TimeEstim
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread
from mtkclient.gui.erasepart_gui import Ui_partitionListWidget


sys.excepthook = trap_exc_during_debug


class EraseFlashWindow(QDialog):
    # Partition
    @Slot()
    def updateEraseState(self):
        totalBytes = 0
        doneBytes = 0
        for partition in self.eraseStatus["allPartitions"]:
            totalBytes = totalBytes + self.eraseStatus["allPartitions"][partition]['size']
            if (self.eraseStatus["allPartitions"][partition]['done'] and partition != self.eraseStatus[
                "currentPartition"]):
                doneBytes = doneBytes + self.eraseStatus["allPartitions"][partition]['size']
        doneBytes = doneBytes + self.eraseStatus["currentPartitionSizeDone"]
        percentageDone = (self.eraseStatus["currentPartitionSizeDone"] / self.eraseStatus["currentPartitionSize"]) * 100
        fullPercentageDone = (doneBytes / totalBytes) * 100
        self.ui.partProgress.setValue(percentageDone)
        timeinfo = self.timeEst.update(doneBytes, totalBytes)
        self.ui.partProgressText.setText("Current partition: " + self.eraseStatus["currentPartition"] + " (" +
                                         convert_size(self.eraseStatus["currentPartitionSizeDone"]) + " / " +
                                         convert_size(self.eraseStatus["currentPartitionSize"])+" -> "+
                                         timeinfo+self.tr(" left")+")")

        self.ui.fullProgress.setValue(fullPercentageDone)
        timetotal = self.timeEstTotal.update(fullPercentageDone, 100)
        self.ui.fullProgressText.setText("Total: (" + convert_size(doneBytes) + " / " +
                                         convert_size(totalBytes)+" -> "+timetotal+self.tr(" left")+")")

    @Slot(int)
    def updateProgress(self, progress):
        self.eraseStatus["currentPartitionSizeDone"] = progress
        self.updateEraseState()

    def updateEraseStateAsync(self, toolkit, parameters):
        while not self.eraseStatus["done"]:
            # print(self.eraseStatus)
            time.sleep(0.1)
        print("DONE")
        self.ui.startBtn.setEnabled(True)

    def erasePartDone(self):
        self.sendToLogSignal.emit("erase done!")

    def selectAll(self):
        if self.ui.SelectAllCheckbox.isChecked():
            for partition in self.partitionCheckboxes:
                self.partitionCheckboxes[partition]['box'].setChecked(True)
        else:
            for partition in self.partitionCheckboxes:
                self.partitionCheckboxes[partition]['box'].setChecked(False)


    def erasePartition(self):
        self.ui.startBtn.setEnabled(False)
        thread = asyncThread(parent=self.parent, n=0, function=self.erasePartitionAsync,parameters=[])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateEraseState)
        thread.sendToProgressSignal.connect(self.updateProgress)
        thread.start()


    def erasePartitionAsync(self, toolkit, parameters):
        self.timeEst.init()
        self.timeEstTotal.init()
        self.sendToLogSignal = toolkit.sendToLogSignal
        toolkit.sendToLogSignal.emit("test")
        self.eraseStatus["done"] = False
        thread = asyncThread(self.parent, 0, self.updateEraseStateAsync, [])
        thread.sendUpdateSignal.connect(self.updateEraseState)
        thread.sendToProgressSignal.connect(self.updateProgress)
        thread.start()
        # calculate total bytes
        self.eraseStatus["allPartitions"] = {}
        for partition in self.partitionCheckboxes:
            if self.partitionCheckboxes[partition]['box'].isChecked():
                self.eraseStatus["allPartitions"][partition] = {"size": self.partitionCheckboxes[partition]['size'],
                                                               "done": False}
        for partition in self.partitionCheckboxes:
            if self.partitionCheckboxes[partition]['box'].isChecked():
                variables = mock.Mock()
                variables.partitionname = partition
                variables.parttype = None
                self.eraseStatus["currentPartitionSize"] = self.partitionCheckboxes[partition]['size']
                self.eraseStatus["currentPartition"] = partition
                self.da_handler.close = self.erasePartDone  # Ignore the normally used sys.exit
                self.da_handler.handle_da_cmds(self.mtkClass, "e", variables)
                self.eraseStatus["allPartitions"][partition]['done'] = True
                # MtkTool.cmd_stage(mtkClass, None, None, None, False)
        self.eraseStatus["done"] = True
        thread.wait()

    def __init__(self, parent, devhandler, da_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(EraseFlashWindow, self).__init__(parent)
        devhandler.sendToProgressSignal.connect(self.updateProgress)
        self.mtkClass = devhandler.mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.eraseStatus = {}
        self.fdialog = FDialog(self)
        self.da_handler = da_handler
        self.timeEst = TimeEstim()
        self.timeEstTotal = TimeEstim()
        #self.setFixedSize(400, 500)
        self.setWindowTitle("Erase partition(s)")

        #partitionListWidget = QWidget(self)
        self.ui = Ui_partitionListWidget()
        self.ui.setupUi(self)

        data, guid_gpt = self.mtkClass.daloader.get_gpt()
        if guid_gpt is None:
            print("Error reading gpt")
            self.ui.title.setText(self.tr("Error reading gpt"))
        else:
            self.ui.title.setText(self.tr("Select partitions to erase"))
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

        self.ui.startBtn.clicked.connect(self.erasePartition)
        self.ui.SelectAllCheckbox.clicked.connect(self.selectAll)
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
