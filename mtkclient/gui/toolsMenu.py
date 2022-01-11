from PySide6.QtCore import Slot, QObject, Signal
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
from mtkclient.gui.toolkit import trap_exc_during_debug, asyncThread, FDialog
from mtkclient.Library.mtk_da_cmd import DA_handler
import os
import sys

sys.excepthook = trap_exc_during_debug

class UnlockMenu(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, ui, parent, devhandler, da_handler: DA_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(UnlockMenu, self).__init__(parent)
        self.parent = parent
        self.ui = ui
        self.fdialog = FDialog(parent)
        self.mtkClass = devhandler.mtkClass
        self.sendToLog = sendToLog
        self.da_handler = da_handler

    @Slot()
    def updateLock(self):
        self.enableButtonsSignal.emit()
        result = self.parent.Status['result'][1]
        self.ui.partProgressText.setText(result)
        self.sendToLogSignal.emit(self.tr(result))

    def unlock(self, unlockflag):
        self.disableButtonsSignal.emit()
        self.ui.partProgressText.setText(self.tr("Generating..."))
        thread = asyncThread(self.parent, 0, self.UnlockAsync, [unlockflag])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateLock)
        thread.start()
        thread.wait()
        self.enableButtonsSignal.emit()

    def UnlockAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.sendUpdateSignal = toolkit.sendUpdateSignal
        toolkit.sendToLogSignal.emit(self.tr("Bootloader: ")+parameters[0])
        self.parent.Status["result"] = self.mtkClass.daloader.seccfg(parameters[0])
        self.parent.Status["done"] = True
        self.sendUpdateSignal.emit()


class generateKeysMenu(QObject):
    enableButtonsSignal = Signal()
    disableButtonsSignal = Signal()

    def __init__(self, ui, parent, devhandler, da_handler: DA_handler, sendToLog):  # def __init__(self, *args, **kwargs):
        super(generateKeysMenu, self).__init__(parent)
        self.parent = parent
        self.ui = ui
        self.fdialog = FDialog(parent)
        self.mtkClass = devhandler.mtkClass
        self.sendToLog = sendToLog
        self.da_handler = da_handler

    @Slot()
    def updateKeys(self):
        path = os.path.join(self.hwparamFolder, "hwparam.json")
        self.ui.keystatuslabel.setText(self.tr(f"Keys saved to {path}."))
        keycount = len(self.parent.Status['result'])
        self.ui.keytable.setRowCount(keycount)
        self.ui.keytable.setColumnCount(2)

        column = 0
        for key in self.parent.Status['result']:
            skey = self.parent.Status['result'][key]
            if skey is not None:
                self.ui.keytable.setItem(column, 0, QTableWidgetItem(key))
                self.ui.keytable.setItem(column, 1, QTableWidgetItem(skey))
                column+=1
        self.sendToLogSignal.emit(self.tr("Keys generated!"))
        self.enableButtonsSignal.emit()

    def generateKeys(self):
        self.ui.keystatuslabel.setText(self.tr("Generating..."))
        hwparamFolder = self.fdialog.opendir(self.tr("Select output directory"))
        if hwparamFolder == "" or hwparamFolder == None:
            self.parent.enablebuttons()
            return
        else:
            self.mtkClass.config.set_hwparam_path(hwparamFolder)
        self.hwparamFolder = hwparamFolder
        thread = asyncThread(self.parent, 0, self.generateKeysAsync, [self.hwparamFolder])
        thread.sendToLogSignal.connect(self.sendToLog)
        thread.sendUpdateSignal.connect(self.updateKeys)
        thread.start()
        self.disableButtonsSignal.emit()


    def generateKeysAsync(self, toolkit, parameters):
        self.sendToLogSignal = toolkit.sendToLogSignal
        self.sendUpdateSignal = toolkit.sendUpdateSignal
        toolkit.sendToLogSignal.emit(self.tr("Generating keys"))
        self.parent.Status["result"] = self.mtkClass.daloader.keys()
        # MtkTool.cmd_stage(mtkClass, None, None, None, False)
        self.parent.Status["done"] = True
        self.sendUpdateSignal.emit()

