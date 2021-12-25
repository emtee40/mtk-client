from PySide2.QtCore import Signal, QThread
from traceback import print_exception


class asyncThread(QThread):
    sendToLogSignal = Signal(str)
    sendUpdateSignal = Signal()

    def __init__(self, parent, n, function, parameters):
        super(asyncThread, self).__init__(parent)
        # self.n = n
        self.parameters = parameters
        self.function = function

    def run(self):
        self.function(self, self.parameters)


def trap_exc_during_debug(type_, value, traceback):
    print(print_exception(type_, value, traceback), flush=True)
    # sendToLog("Error: "+str(value))
    # when app raises uncaught exception, print info
    # print("OH NO")
    # print(args)
    # print(traceback.print_tb(exc_traceback))
    # print(traceback.format_exc())
