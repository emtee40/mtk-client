import sys
import time
import mtk
import mock
import logging
import traceback

from PyQt5.QtCore import *
from PyQt5.QtGui import QTextOption, QPixmap
from PyQt5.QtWidgets import *

class guiLogger:
    global guiState;
    def info(text):
        sendToLog(text)
        #grab useful stuff from this log
        #if ("\tCPU:" in text):
        #    phoneInfo['chipset'] = text.replace("\t","").replace("CPU:","").replace("()","")
        #elif ("BROM mode detected" in text):
        #    phoneInfo['bootMode'] = "In Bootrom"
        #if (guiState == "welcome") and (phoneInfo['chipset'] is not ""):
        #    phoneInfoTextbox.setText("Phone detected:\n" + phoneInfo['chipset']+"\n"+phoneInfo['bootMode']);
    def debug(text):
        sendToLog(text)
    def error(text):
        sendToLog(text)
    def setLevel(logLevel):
        return True;

#Initiate MTK classes
variables = mock.Mock()
variables.cmd = "stage"
variables.debugmode = True
config = mtk.Mtk_Config(loglevel=logging.INFO)
MtkTool = mtk.Main(variables)
mtkClass = mtk.Mtk(config=config, loglevel=logging.INFO, guiLogger=guiLogger)

def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)
    print(traceback.format_exc())

# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

guiState = "welcome"
phoneInfo = {"chipset": "", "bootMode": ""};

class asyncThread(QThread):
    sendToLog = pyqtSignal(str);
    def __init__(self, parent, n, function):
        super(asyncThread, self).__init__(parent)
        self.n = n
        self.function = function;
    def run(self):
        self.function(self);

def getDevInfo(self):
    global MtkTool;
    global mtkClass;
    self.sendToLog.emit("test");

    if mtkClass.preloader.init():
        #device should now be connected, get the info
        phoneInfo['chipset'] = mtkClass.config.cpu;
        if (mtkClass.config.is_brom):
            phoneInfo['bootMode'] = "Bootrom mode"
        else:
            phoneInfo['bootMode'] = "Preloader mode"
        phoneInfoTextbox.setText("Phone detected:\n" + phoneInfo['chipset'] + "\n" + phoneInfo['bootMode']);
        status.setText("Device connected :)")
        pixmap = QPixmap("gui/images/phone_connected.png").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation);
        pixmap.setDevicePixelRatio(2.0);
        pic.setPixmap(pixmap)
    try:
        print(mtkClass.daloader.get_partition_data(parttype="user"))
    except Exception:
        print(traceback.format_exc())
    #MtkTool.cmd_stage(mtkClass, None, None, None, False);

def sendToLog(info):
        t = time.localtime();
        logBox.appendPlainText(time.strftime("[%H:%M:%S", t)+"]: "+info)
        logBox.verticalScrollBar().setValue(logBox.verticalScrollBar().maximum())
def openReadflashWindow(q):
        status.setText("OH YEAH"+str(q.text()));
        readFlashWindowVal = ReadFlashWindow()
        #w.close();

class ReadFlashWindow(QWidget):
    #Partition
    @pyqtSlot()
    def getGPTInfo(self):
        global MtkTool;
        global mtkClass;
        self.sendToLog.emit("test");
        MtkTool.cmd_stage(mtkClass, None, None, None, False);
    def __init__(self, *args, **kwargs):
        super(ReadFlashWindow, self).__init__(*args, **kwargs)
        self.setFixedSize(400, 400);
        #widget = QWidget()
        self.setWindowTitle("Read Flash")
        self.show();

        w.setCentralWidget(self)
        print("Jeuj");

if __name__ == '__main__':
    #Init the app window
    app = QApplication(sys.argv)
    win = QMainWindow()
    w = QWidget()

    w.setFixedSize(600,400);
    w.setWindowTitle("MTKTools - Version 2.0 beta")

    #Menubar
    menuBar = QMenuBar(w)
    readFlashMenu = menuBar.addMenu("&Read Flash")
    readFlashMenu.addAction("Read partition(s)")
    #readPartitions = QAction("Read partition(s)", w)
    #readFlashMenu.addAction(readPartitions)
    readFlashMenu.triggered[QAction].connect(openReadflashWindow)
    readFlashMenu.addAction("Read full flash")
    readFlashMenu.addAction("Read offset")

    writeFlashMenu = menuBar.addMenu("&Write Flash")
    writeFlashMenu.addAction("Write partition(s)")
    writeFlashMenu.addAction("Write full flash")
    writeFlashMenu.addAction("Write offset")

    eraseFlashMenu = menuBar.addMenu("&Erase Flash")
    eraseFlashMenu.addAction("Erase partition(s)")
    eraseFlashMenu.addAction("Erase bootsectors")
    menuBar.show();

    #titles
    title = QLabel(w)
    title.setText("MTKTools v2.0");
    title.setGeometry(10,0,480,40);
    title.setStyleSheet("font-size: 17px;");
    title.show();

    # status info
    status = QLabel(w)
    status.setAlignment(Qt.AlignLeft|Qt.AlignTop)
    status.setText("Please connect a Mediatek phone to continue.\n\nHint: Power off the phone before connecting.\n" + \
                                  "For brom mode, press and hold vol up, vol dwn, or all hw buttons " + \
                                  "and connect usb.\n" +
                                  "For preloader mode, don't press any hw button and connect usb.");
    status.setGeometry(10, 30, 465, 256);
    status.setWordWrap(True);
    status.setStyleSheet("font-size: 12px; vertical-align: top;");
    status.show();

    #Device info
    #phone icon
    pic = QLabel(w)
    pixmap = QPixmap("gui/images/phone_notfound.png").scaled(128,128, Qt.KeepAspectRatio, Qt.SmoothTransformation);
    pixmap.setDevicePixelRatio(2.0);
    pic.setPixmap(pixmap)
    pic.resize(pixmap.width()/2, pixmap.height()/2)
    pic.move(545, 10);
    pic.show()

    # phone info
    phoneInfoTextbox = QLabel(w)
    phoneInfoTextbox.setText("No phone found");
    phoneInfoTextbox.setGeometry(10, 10, 520, 100);
    phoneInfoTextbox.setAlignment(Qt.AlignRight | Qt.AlignTop)
    phoneInfoTextbox.setStyleSheet("font-size: 12px;");
    phoneInfoTextbox.show();

    #Line
    line = QFrame(w)
    line.setGeometry(QRect(10, 105, 580, 20))
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)

    #Copyright info
    copyrightInfo = QLabel(w)
    copyrightInfo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    copyrightInfo.setText("Made by: Bjoern Kerler\n" + \
                   "Credits: \n" + \
                   "kamakiri [xyzz]\n" +
                   "linecode exploit [chimera]\n" +
                   "Chaosmaster\n" +
                   "Cygnusx (Gui)\n" +
                   "and all contributers");
    copyrightInfo.setGeometry(10, 125, 405, 256);
    copyrightInfo.setWordWrap(True);
    copyrightInfo.setStyleSheet("font-size: 12px; color: #333; vertical-align: top;");
    copyrightInfo.show();

    def showDebugInfo():
        logBox.show();
        if w.frameGeometry().height() < 500:
            w.setFixedSize(600, 700);
            debugBtn.setText("Hide debug info")
        else:
            w.setFixedSize(600, 400);
            debugBtn.setText("Show debug info")
    #debug
    debugBtn = QPushButton(w);
    debugBtn.setText("Show debug info")
    debugBtn.clicked.connect(showDebugInfo)
    debugBtn.setGeometry((600-150-10),(400-30-10),150,30);
    debugBtn.show();

    logBox = QPlainTextEdit(w);
    logBox.setGeometry(11,(700-280-10),578,280);
    logBox.setWordWrapMode(QTextOption.NoWrap);
    logBox.setReadOnly(True);

    w.show();

    #Get the device info
    thread = asyncThread(app, 0, getDevInfo)
    thread.sendToLog.connect(sendToLog);
    thread.start();

    #Run loop the app
    app.exec();
    #Prevent thread from not being closed and call error end codes
    thread.terminate()
    thread.wait()
