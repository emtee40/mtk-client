import math
import os
from PySide2.QtCore import Signal, QThread, Slot, Property
from PySide2.QtWidgets import QFileDialog, QCheckBox
from traceback import print_exception


class CheckBox(QCheckBox):
    def __init__( self, *args ):
        super(CheckBox, self).__init__(*args)
        self._readOnly = False

    def isReadOnly( self ):
        return self._readOnly

    def mousePressEvent( self, event ):
        if self.isReadOnly():
            event.accept()
        else:
            super(CheckBox, self).mousePressEvent(event)

    def mouseMoveEvent( self, event ):
        if self.isReadOnly():
            event.accept()
        else:
            super(CheckBox, self).mouseMoveEvent(event)

    def mouseReleaseEvent( self, event ):
        if self.isReadOnly():
            event.accept()
        else:
            super(CheckBox, self).mouseReleaseEvent(event)

    def keyPressEvent( self, event ):
        if self.isReadOnly():
            event.accept()
        else:
            super(CheckBox, self).keyPressEvent(event)

    @Slot(bool)
    def setReadOnly( self, state ):
        self._readOnly = state

    readOnly = Property(bool, isReadOnly, setReadOnly)

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


class asyncThread(QThread):
    sendToLogSignal = Signal(str)
    sendUpdateSignal = Signal()
    sendToProgressSignal = Signal(int)

    def __init__(self, parent, n, function, parameters):
        super(asyncThread, self).__init__(parent)
        # self.n = n
        self.parameters = parameters
        self.function = function

    def run(self):
        self.function(self, self.parameters)

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

    def open(self, filename=""):
        fname = os.path.join(self.lastpath, filename)
        ret = QFileDialog.getOpenFileName(parent=self.parent, caption=self.parent.tr("Select input file"), dir=fname,
                                          filter="Binary dump (*.bin)")
        if ret:
            fname = ret[0]
            if fname != "":
                self.lastpath = os.path.dirname(fname)
                return fname
        return None

    def opendir(self,caption):
        fname = os.path.join(self.lastpath)
        fdir=QFileDialog.getExistingDirectory(parent=self.parent, dir=fname,
                                              caption=self.parent.tr(caption))
        if fdir != "":
            return fdir
        return None

def trap_exc_during_debug(type_, value, traceback):
    print(print_exception(type_, value, traceback), flush=True)
    # sendToLog("Error: "+str(value))
    # when app raises uncaught exception, print info
    # print("OH NO")
    # print(args)
    # print(traceback.print_tb(exc_traceback))
    # print(traceback.format_exc())
