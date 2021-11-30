import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QTextOption
import sys

class asyncThread(QThread):
    sendToLog = pyqtSignal(str);
    def __init__(self, parent, n, function):
        super(asyncThread, self).__init__(parent)
        self.n = n
        self.function = function;
    def run(self):
        self.function(self);

def getDevInfo(self):
    print("test");
#Init the app window
app = QApplication(sys.argv)
w = QWidget()
w.setFixedSize(500,600);
w.setWindowTitle("MTKTools v2.0")

logBox = QPlainTextEdit(w);
logBox.setGeometry(11,150,478,410);
logBox.setWordWrapMode(QTextOption.NoWrap);
logBox.setReadOnly(True);
logBox.show();
w.show();

def sendToLog(info):
    t = time.localtime();
    logBox.appendPlainTexT(time.strftime("[%H:%M:%S", t)+"]: "+info)

#Get the device info
thread = asyncThread(app, 0, getDevInfo)
thread.sendToLog.connect(sendToLog);
thread.start();

#Run loop the app
app.exec();