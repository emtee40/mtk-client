from random import random

from PySide2.QtCore import Slot, Qt
from PySide2.QtGui import QTextOption, QPixmap
from PySide2.QtWidgets import *
import mock
from mtkclient.gui.toolkit import *
import os
import sys
import time

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
        self.partProgress.setValue(percentageDone)
        self.partProgressText.setText("Current partition: " + self.dumpStatus["currentPartition"] + " (" + str(
            round((self.dumpStatus["currentPartitionSizeDone"] / 1024 / 1024))) + "Mb / " + str(
            round((self.dumpStatus["currentPartitionSize"] / 1024 / 1024))) + " Mb)")

        self.fullProgress.setValue(fullPercentageDone)
        self.fullProgressText.setText("Total: (" + str(round((doneBytes / 1024 / 1024))) + "Mb / " + str(
            round((totalBytes / 1024 / 1024))) + " Mb)")

    def updateDumpStateAsync(self, toolkit, parameters):
        while not self.dumpStatus["done"]:
            # print(self.dumpStatus)
            time.sleep(0.1)
            try:
                self.dumpStatus["currentPartitionSizeDone"] = os.stat(self.dumpStatus["currentPartitionFile"]).st_size
                toolkit.sendUpdateSignal.emit()
                # self.partProgressText.setText(str(currentPartitionSize)+"Current pa"+str(random(0,100000))+"rtition: "+self.dumpStatus["currentPartition"])
            except:
                time.sleep(0.1)
        print("DONE")
        self.startBtn.setEnabled(True)

    def dumpPartDone(self):
        self.sendToLogSignal.emit("dump klaar!")

    def dumpPartition(self):
        self.startBtn.setEnabled(False)
        self.dumpFolder = str(QFileDialog.getExistingDirectory(self, "Select output directory"))
        # self.startBtn.setText("In progress..")
        thread = asyncThread(self, 0, self.dumpPartitionAsync, [])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateDumpState)
        thread.start()


    def dumpPartitionAsync(self, toolkit, parameters):
        # global MtkTool
        # global mtkClass
        self.sendToLogSignal = toolkit.sendToLogSignal
        toolkit.sendToLogSignal.emit("test")
        # partitionname = args.partitionname
        # parttype = args.parttype
        # filename = args.filename
        # print(self.partitionCheckboxes)
        self.dumpStatus["done"] = False
        thread = asyncThread(self, 0, self.updateDumpStateAsync, [])
        thread.sendUpdateSignal.connect(self.updateDumpState)
        thread.start()
        # calculate total bytes
        self.dumpStatus["allPartitions"] = {}
        # for partition in self.partitionCheckboxes:
        #    if self.partitionCheckboxes[partition]['box'].isChecked():
        #        self.dumpStatus["totalSize"] = self.dumpStatus["totalSize"]+self.partitionCheckboxes[partition]['size']
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
        self.dumpStatus["done"] = True

    def __init__(self, parent, mtkClass, da_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(ReadFlashWindow, self).__init__(parent)
        self.mtkClass = mtkClass
        self.sendToLog = sendToLog
        self.dumpStatus = {}
        self.da_handler = da_handler
        self.setFixedSize(400, 500)
        # widget = QWidget()
        self.setWindowTitle("Read partition(s)")

        title = QLabel(self)
        title.setGeometry(10, 0, 480, 40)

        data, guid_gpt = self.mtkClass.daloader.get_gpt()
        if guid_gpt is None:
            print("Error reading gpt")
            title.setText("Error reading gpt")
        else:
            title.setText("Select partitions to dump")
            # guid_gpt.print()
            position = 40
            partitionList = QScrollArea(self)
            # partitionList.setFrameShape(frame)
            partitionListWidget = QWidget(self)
            partitionListWidgetVBox = QVBoxLayout()
            partitionListWidget.setLayout(partitionListWidgetVBox)
            partitionList.setWidget(partitionListWidget)
            # partitionListWidget.addWidget(partitionList)
            partitionList.setWidgetResizable(True)
            # partitionListWidget = QWidget(partitionList)
            # partitionListWidget.size(1000, 900)
            partitionList.setGeometry(10, 40, 380, 320)

            partitionList.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            partitionList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            # partitionList.setWidget(self)
            self.partitionCheckboxes = {}
            print(self.partitionCheckboxes)
            for partition in guid_gpt.partentries:
                # print(partition.name)
                # print()
                self.partitionCheckboxes[partition.name] = {}
                self.partitionCheckboxes[partition.name]['size'] = (partition.sectors * guid_gpt.sectorsize)
                self.partitionCheckboxes[partition.name]['box'] = QCheckBox()
                self.partitionCheckboxes[partition.name]['box'].setText(partition.name + " (" + str(
                    round(((partition.sectors * guid_gpt.sectorsize) / 1024 / 1024), 1)) + " Mb)")
                partitionListWidgetVBox.addWidget(self.partitionCheckboxes[partition.name]['box'])
        # partition progress bar
        self.partProgressText = QLabel(self)
        self.partProgressText.setText("Ready to start...")
        self.partProgressText.setGeometry(10, 355, 480, 40)
        self.partProgress = QProgressBar(self)
        self.partProgress.setValue(0)
        self.partProgress.setGeometry(10, 390, 380, 20)
        self.partProgress.show()

        # full progress bar
        self.fullProgressText = QLabel(self)
        self.fullProgressText.setText("")
        self.fullProgressText.setGeometry(10, 405, 480, 40)
        self.fullProgress = QProgressBar(self)
        self.fullProgress.setValue(0)
        self.fullProgress.setGeometry(10, 430, 380, 20)
        self.fullProgress.show()

        # start button
        self.startBtn = QPushButton(self)
        self.startBtn.setText("Start dumping")
        self.startBtn.clicked.connect(self.dumpPartition)
        self.startBtn.setGeometry((400 - 240 - 150), (500 - 30 - 10), 150, 30)
        self.startBtn.show()

        self.CloseBtn = QPushButton(self)
        self.CloseBtn.setText("Close")
        self.CloseBtn.clicked.connect(self.close)
        self.CloseBtn.setGeometry((400 - 60), (500 - 30 - 10), 50, 30)
        self.CloseBtn.show()

        self.show()
        # parent.setCentralWidget(self)
