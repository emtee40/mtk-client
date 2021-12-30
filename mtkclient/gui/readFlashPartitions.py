from random import random

from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QDialog, QFileDialog, QCheckBox, QVBoxLayout, QSizePolicy, QWidget
import mock
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread
from mtkclient.gui.readpart_gui import Ui_partitionListWidget
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
        self.ui.partProgress.setValue(percentageDone)
        self.ui.partProgressText.setText("Current partition: " + self.dumpStatus["currentPartition"] + " (" + str(
            round((self.dumpStatus["currentPartitionSizeDone"] / 1024 / 1024))) + "Mb / " + str(
            round((self.dumpStatus["currentPartitionSize"] / 1024 / 1024))) + " Mb)")

        self.ui.fullProgress.setValue(fullPercentageDone)
        self.ui.fullProgressText.setText("Total: (" + str(round((doneBytes / 1024 / 1024))) + "Mb / " + str(
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
        self.ui.startBtn.setEnabled(True)

    def dumpPartDone(self):
        self.sendToLogSignal.emit("dump done!")

    def selectAll(self):
        if self.ui.SelectAllCheckbox.isChecked():
            for partition in self.partitionCheckboxes:
                self.partitionCheckboxes[partition]['box'].setChecked(True);
        else:
            for partition in self.partitionCheckboxes:
                self.partitionCheckboxes[partition]['box'].setChecked(False);


    def dumpPartition(self):
        self.ui.startBtn.setEnabled(False)
        self.dumpFolder = str(QFileDialog.getExistingDirectory(self, "Select output directory"))
        # self.startBtn.setText("In progress..")
        thread = asyncThread(parent=self, n=0, function=self.dumpPartitionAsync,parameters=[])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateDumpState)
        thread.start()


    def dumpPartitionAsync(self, toolkit, parameters):
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
        if self.ui.DumpGPTCheckbox.isChecked():
            #also dump the GPT
            variables = mock.Mock()
            variables.directory = self.dumpFolder
            variables.parttype = None
            self.dumpStatus["allPartitions"]["GPT"] = {};
            self.dumpStatus["allPartitions"]["GPT"]['size'] = 17;
            self.dumpStatus["currentPartition"] = "GPT"
            self.da_handler.close = self.dumpPartDone  # Ignore the normally used sys.exit
            self.da_handler.handle_da_cmds(self.mtkClass, "gpt", variables)
            self.dumpStatus["allPartitions"]["GPT"]['done'] = True
        self.dumpStatus["done"] = True
        thread.wait()

    def __init__(self, parent, mtkClass, da_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(ReadFlashWindow, self).__init__(parent)
        self.mtkClass = mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.dumpStatus = {}
        self.da_handler = da_handler
        #self.setFixedSize(400, 500)
        self.setWindowTitle("Read partition(s)")

        #partitionListWidget = QWidget(self)
        self.ui = Ui_partitionListWidget()
        self.ui.setupUi(self)

        data, guid_gpt = self.mtkClass.daloader.get_gpt()
        if guid_gpt is None:
            print("Error reading gpt")
            self.ui.title.setText("Error reading gpt")
        else:
            self.ui.title.setText("Select partitions to dump")
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
                self.partitionCheckboxes[partition.name]['box'].setText(partition.name + " (" + str(
                    round(((partition.sectors * guid_gpt.sectorsize) / 1024 / 1024), 1)) + " Mb)")
                partitionListWidgetVBox.addWidget(self.partitionCheckboxes[partition.name]['box'])

        self.ui.startBtn.clicked.connect(self.dumpPartition)
        self.ui.SelectAllCheckbox.clicked.connect(self.selectAll);
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
