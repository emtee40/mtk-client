from PyQt5.QtCore import *
from traceback import print_exception

class asyncThread(QThread):
    sendToLogSignal = pyqtSignal(str);
    sendUpdateSignal = pyqtSignal();
    def __init__(self, parent, n, function):
        super(asyncThread, self).__init__(parent)
        self.n = n
        self.function = function;
    def run(self):
        self.function(self);
def trap_exc_during_debug(type_, value, traceback):
    print(print_exception(type_, value, traceback), flush=True)
    #sendToLog("Error: "+str(value));
    # when app raises uncaught exception, print info
    #print("OH NO")
    #print(args)
    #print(traceback.print_tb(exc_traceback))
    #print(traceback.format_exc())