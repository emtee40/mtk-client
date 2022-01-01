from PySide6.QtCore import Slot, QObject
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread, FDialog
from mtkclient.Library.mtk_da_cmd import DA_handler
import os
import sys

sys.excepthook = trap_exc_during_debug

class generateKeysMenu(QObject):
    # Partition

    @Slot()
    def updateKeys(self):
        path = os.path.join(self.hwparamFolder, "hwparam.json")
        self.ui.keystatuslabel.setText(self.tr(f"Keys saved to {path}."))
        self.ui.generatekeybtn.setEnabled(True)
        keycount = len(self.keysStatus['result'])
        self.ui.keytable.setRowCount(keycount)
        self.ui.keytable.setColumnCount(2)

        column = 0
        for key in self.keysStatus['result']:
            skey = self.keysStatus['result'][key]
            if skey is not None:
                self.ui.keytable.setItem(column, 0, QTableWidgetItem(key))
                self.ui.keytable.setItem(column, 1, QTableWidgetItem(skey))
                column+=1
        self.sendToLogSignal.emit(self.tr("Keys generated!"))

    def generateKeys(self):
        self.ui.generatekeybtn.setEnabled(False)
        self.ui.keystatuslabel.setText(self.tr("Generating..."))
        hwparamFolder = self.fdialog.opendir(self.tr("Select output directory"))
        if hwparamFolder == "":
            self.ui.generatekeybtn.setEnabled(True)
            return
        else:
            self.mtkClass.config.set_hwparam_path(hwparamFolder)
        self.hwparamFolder = hwparamFolder
        thread = asyncThread(self.parent, 0, self.generateKeysAsync, [self.hwparamFolder])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateKeys)
        thread.start()

    def generateKeysAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.sendUpdateSignal = toolkit.sendUpdateSignal
        toolkit.sendToLogSignal.emit(self.tr("Generating keys"))
        self.keysStatus["result"] = self.mtkClass.daloader.keys()
        # MtkTool.cmd_stage(mtkClass, None, None, None, False)
        self.keysStatus["done"] = True
        self.sendUpdateSignal.emit()

    def __init__(self, ui, parent, devhandler, da_handler: DA_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(generateKeysMenu, self).__init__(parent)
        self.parent = parent
        self.ui = ui
        self.fdialog = FDialog(parent)
        self.mtkClass = devhandler.mtkClass
        self.sendToLog = sendToLog
        self.keysStatus = {}
        self.da_handler = da_handler
