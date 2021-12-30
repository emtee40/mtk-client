import os
import sys
import time
import mock
from functools import partial
from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, \
                              QPushButton
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread, convert_size, FDialog, CheckBox, TimeEstim
from mtkclient.gui.writepart_gui import Ui_writepartitionListWidget

sys.excepthook = trap_exc_during_debug


class WriteFlashWindow(QDialog):
    # Partition
    @Slot()
    def updateWriteState(self):
        totalBytes = 0
        doneBytes = 0
        for partition in self.writeStatus["allPartitions"]:
            totalBytes = totalBytes + self.writeStatus["allPartitions"][partition]['size']
            if self.writeStatus["allPartitions"][partition]['done'] and partition != self.writeStatus[
                "currentPartition"]:
                doneBytes = doneBytes + self.writeStatus["allPartitions"][partition]['size']
        doneBytes = doneBytes + self.writeStatus["currentPartitionSizeDone"]
        percentageDone = (self.writeStatus["currentPartitionSizeDone"] / self.writeStatus["currentPartitionSize"]) * 100
        fullPercentageDone = (doneBytes / totalBytes) * 100
        self.ui.partProgress.setValue(percentageDone)
        timeinfo = self.timeEst.update(doneBytes, totalBytes)
        self.ui.partProgressText.setText("Current partition: " + self.writeStatus["currentPartition"] + " (" +
                                         convert_size(self.writeStatus["currentPartitionSizeDone"]) + " / " +
                                         convert_size(self.writeStatus["currentPartitionSize"]) +
                                         timeinfo + self.tr(" left") + ")")
        timeinfototal = self.timeEstTotal.update(fullPercentageDone, 100)
        self.ui.fullProgress.setValue(fullPercentageDone)
        self.ui.fullProgressText.setText("Total: (" + convert_size(doneBytes) + " / " + convert_size(totalBytes)+
                                         timeinfototal + self.tr(" left") + ")")

    @Slot(int)
    def updateProgress(self, progress):
        self.writeStatus["currentPartitionSizeDone"] = progress
        self.updateWriteState()

    def updateWriteStateAsync(self, toolkit, parameters):
        while not self.writeStatus["done"]:
            time.sleep(0.1)
        print("DONE")
        self.ui.startBtn.setEnabled(True)

    def writePartDone(self):
        self.sendToLogSignal.emit("write done!")

    def selectFiles(self):
        self.folder = self.fdialog.opendir(self.tr("Select input directory"))
        if self.folder:
            for partition in self.partitionCheckboxes:
                checkbox, lineedit, button = self.partitionCheckboxes[partition]['box']
                for root, dirs, files in os.walk(self.folder):
                    for file in files:
                        if file in [partition+".bin",partition+".img"]:
                            lineedit.setText(os.path.join(root,file))
                            lineedit.setDisabled(False)
                            checkbox.setChecked(True)
                            break
                    break

    def writePartition(self):
        self.ui.startBtn.setEnabled(False)
        thread = asyncThread(parent=self.parent, n=0, function=self.writePartitionAsync,parameters=[])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateWriteState)
        thread.sendToProgressSignal.connect(self.updateProgress)
        thread.start()

    def openFile(self, partition, checkbox, lineedit):
        fname=self.fdialog.open(partition+".img")
        if fname is None:
            checkbox.setChecked(False)
            lineedit.setText("")
            lineedit.setDisabled(True)
            return ""
        checkbox.setChecked(True)
        lineedit.setText(fname)
        lineedit.setDisabled(False)
        return fname

    def writePartitionAsync(self, toolkit, parameters):
        self.timeEst.init()
        self.timeEstTotal.init()
        self.sendToLogSignal = toolkit.sendToLogSignal
        toolkit.sendToLogSignal.emit("test")
        # partitionname = args.partitionname
        # parttype = args.parttype
        # filename = args.filename
        # print(self.partitionCheckboxes)
        self.writeStatus["done"] = False
        thread = asyncThread(self.parent, 0, self.updateWriteStateAsync, [])
        thread.sendUpdateSignal.connect(self.updateWriteState)
        thread.sendToProgressSignal.connect(self.updateProgress)
        thread.start()
        # calculate total bytes
        self.writeStatus["allPartitions"] = {}
        for partition in self.partitionCheckboxes:
            checkbox, lineedit, button = self.partitionCheckboxes[partition]['box']
            if checkbox.isChecked():
                self.writeStatus["allPartitions"][partition] = {"size": self.partitionCheckboxes[partition]['size'],
                                                               "done": False}
        for partition in self.partitionCheckboxes:
            checkbox, lineedit, button = self.partitionCheckboxes[partition]['box']
            if checkbox.isChecked():
                variables = mock.Mock()
                variables.partitionname = partition
                variables.filename = lineedit.text()
                variables.parttype = "user"
                self.writeStatus["currentPartitionSize"] = self.partitionCheckboxes[partition]['size']
                self.writeStatus["currentPartition"] = partition
                self.writeStatus["currentPartitionFile"] = variables.filename
                self.da_handler.close = self.writePartDone  # Ignore the normally used sys.exit
                self.da_handler.handle_da_cmds(self.mtkClass, "w", variables)
                self.writeStatus["allPartitions"][partition]['done'] = True
                # MtkTool.cmd_stage(mtkClass, None, None, None, False)
        self.writeStatus["done"] = True
        thread.wait()

    def __init__(self, parent, devhandler, da_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(WriteFlashWindow, self).__init__(parent)
        devhandler.sendToProgressSignal.connect(self.updateProgress)
        self.mtkClass = devhandler.mtkClass
        self.parent = parent.parent()
        self.sendToLog = sendToLog
        self.writeStatus = {}
        self.fdialog = FDialog(self)
        self.da_handler = da_handler
        self.timeEst = TimeEstim()
        self.timeEstTotal = TimeEstim()
        #self.setFixedSize(400, 500)
        self.setWindowTitle("Write partition(s)")

        #partitionListWidget = QWidget(self)
        self.ui = Ui_writepartitionListWidget()
        self.ui.setupUi(self)

        data, guid_gpt = self.mtkClass.daloader.get_gpt()
        self.guid_gpt = guid_gpt
        if guid_gpt is None:
            print("Error reading gpt")
            self.ui.title.setText("Error reading gpt")
        else:
            self.ui.title.setText("Select partitions to write")
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
                vb = QVBoxLayout()
                qc=CheckBox()
                qc.setReadOnly(True)
                qc.setText(partition.name + " (" + convert_size(partition.sectors * guid_gpt.sectorsize) + ")")
                hc=QHBoxLayout()
                ll=QLineEdit()
                lb=QPushButton(self.tr("Set"))
                lb.clicked.connect(partial(self.openFile,partition.name,qc,ll))
                hc.addWidget(ll)
                hc.addWidget(lb)
                vb.addWidget(qc)
                vb.addLayout(hc)
                ll.setDisabled(True)
                self.partitionCheckboxes[partition.name]['box'] = [qc,ll,lb]
                partitionListWidgetVBox.addLayout(vb)

        self.ui.startBtn.clicked.connect(self.writePartition)
        self.ui.selectfromdir.clicked.connect(self.selectFiles)
        self.ui.closeBtn.clicked.connect(self.close)
        self.show()
