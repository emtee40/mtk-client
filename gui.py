import sys
import time
import mtk
from mtkclient.Library.mtk_da_cmd import DA_handler
import mock
import logging

import ctypes
from PyQt5.QtCore import *
from PyQt5.QtGui import QTextOption, QPixmap, QTransform, QIcon
from PyQt5.QtWidgets import *
from gui.readFlashPartitions import *
from gui.toolkit import *
import traceback
import math

# TO do Move all GUI modifications to signals!

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

# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

#Initiate MTK classes
variables = mock.Mock()
variables.cmd = "stage"
variables.debugmode = True
config = mtk.Mtk_Config(loglevel=logging.INFO)
config.gpt_settings = mtk.gpt_settings(0,0,0)  #This actually sets the right GPT settings..
#if sys.platform.startswith('darwin'):
#    config.ptype = "kamakiri" #Temp for Mac testing
MtkTool = mtk.Main(variables)
mtkClass = mtk.Mtk(config=config, loglevel=logging.INFO, guiLogger=guiLogger)
loglevel = logging.INFO
da_handler = DA_handler(mtkClass, loglevel)

guiState = "welcome"
phoneInfo = {"chipset": "", "bootMode": "", "daInit": False, "cdcInit": False};

def getDevInfo(self, parameters):
    print(parameters);
    mtkClass = parameters[0];
    da_handler = parameters[1];
    phoneInfo = parameters[2];
    #global MtkTool;
    #global mtkClass;
    #global da_handler;
    #global phoneInfo;
    try:
        if mtkClass.port.cdc.connect() == False:
            try:
                phoneInfo['cdcInit'] = True;
                mtkClass.preloader.init()
            except:
                print("OH NO 1");
            # device should now be connected, get the info
            phoneInfo['chipset'] = str(mtkClass.config.cpu);
            phoneInfo['chipset'] = str(mtkClass.config.chipconfig.name) + " (" + str(mtkClass.config.chipconfig.description) + ")";
            if (mtkClass.config.is_brom):
                phoneInfo['bootMode'] = "Bootrom mode"
            elif (mtkClass.config.chipconfig.damode):
                phoneInfo['bootMode'] = "DA mode"
            else:
                phoneInfo['bootMode'] = "Preloader mode"
            #phoneInfoTextbox.setText("Phone detected:\n" + phoneInfo['chipset'] + "\n" + phoneInfo['bootMode']);
            self.sendUpdateSignal.emit();
            #print(mtkClass.port.cdc.detectusbdevices());
            #mtkClass.port.cdc.connect();
            #self.sendToLogSignal.emit(str(mtkClass.port.cdc.connected));
            #time.sleep(0.5);
    except:
        phoneInfo['cdcInit'] = False;
        self.sendUpdateSignal.emit();
    self.sendToLogSignal.emit("CONNECTING!");
    #phoneInfoTextbox.setText("Phone detected:\nReading info...");
    #mtkClass.port.cdc.close(True);
    #time.sleep(0.3)
    #print(mtkClass.port.cdc.connect());
    #if mtkClass.preloader.init(): #This will be run by other commands, so.

    #mtkClass.port.cdc.connected = False;
    try:
        res = da_handler.configure_da(mtkClass, preloader=None)
    except:
        print("OH NO 2");
    if res != False:
        phoneInfo['daInit'] = True
        self.sendUpdateSignal.emit();
    #try:
    #    print(mtkClass.daloader.get_partition_data(parttype="user"))
    #except Exception:
    #    print(traceback.format_exc())
    #MtkTool.cmd_stage(mtkClass, None, None, None, False);

def sendToLog(info):
        t = time.localtime();
        logBox.appendPlainText(time.strftime("[%H:%M:%S", t)+"]: "+info)
        logBox.verticalScrollBar().setValue(logBox.verticalScrollBar().maximum())

def updateGui():
    global phoneInfo;
    phoneInfoTextbox.setText("Phone detected:\n" + phoneInfo['chipset'] + "\n" + phoneInfo['bootMode']);
    status.setText("Device detected, please wait.\nThis can take a while...")
    if phoneInfo['daInit'] == True:
        status.setText("Device connected :)")
        menuBar.setEnabled(True);
        pixmap = QPixmap("gui/images/phone_connected.png").scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation);
        pixmap.setDevicePixelRatio(2.0);
        pic.setPixmap(pixmap)
        spinnerAnim.stop()
        spinner_pic.setHidden(True);
    else:
        if phoneInfo['cdcInit'] == False:
            status.setText("Error initialising. Did you install the drivers?")
        spinnerAnim.start()
        spinner_pic.setHidden(False);
def openReadflashWindow(q):
    #status.setText("OH YEAH"+str(q.text()));
    readFlashWindowVal = ReadFlashWindow(w, mtkClass,da_handler,sendToLog)
    #w.close();

if __name__ == '__main__':
    #Init the app window
    app = QApplication(sys.argv)
    win = QMainWindow()
    icon = QIcon();
    icon.addFile('gui/images/logo_32.png', QSize(32, 32))
    icon.addFile('gui/images/logo_64.png', QSize(64, 64))
    icon.addFile('gui/images/logo_256.png', QSize(256,256))
    icon.addFile('gui/images/logo_512.png', QSize(512, 512))
    app.setWindowIcon(icon)
    win.setWindowIcon(icon)
    if sys.platform.startswith('win'):
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('MTKTools.Gui')
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    dpiMultiplier = win.logicalDpiX();
    if dpiMultiplier == 72:
        dpiMultiplier = 2;
    else:
        dpiMultiplier = 1;
    addTopMargin = 20;
    if sys.platform.startswith('darwin'): #MacOS has the toolbar in the top bar insted of in the app...
        addTopMargin = 0;
    win.setFixedSize(600, 400+addTopMargin);
    w = QWidget(win)
    w.move(0,addTopMargin)

    w.setFixedSize(600,400);
    win.setWindowTitle("MTKClient - Version 2.0 beta")
    #lay = QVBoxLayout(self)

    #Menubar
    menuBar = QMenuBar()
    menuBar.setEnabled(False);
    win.setMenuBar(menuBar)
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
    title.setText("MTKClient v2.0");
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
    pic.resize(int(pixmap.width()/2), int(pixmap.height()/2))
    pic.move(545, 10);
    pic.show()

    # phone spinner
    spinner_pic = QLabel(w)
    pixmap = QPixmap("gui/images/phone_loading.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation);
    pixmap.setDevicePixelRatio(2.0);
    #trans = QTransform();
    #trans.rotate(90);
    spinner_pic.setPixmap(pixmap)
    spinner_pic.resize(int(pixmap.width() / 2), int(pixmap.height() / 2))
    spinner_pic.move(551, 25);
    spinner_pic.show()
    def spinnerAnimRot(angle: QVariant):
        #print(angle);
        trans = QTransform();
        #trans.translate(pixmap.width()+angle / 2, pixmap.height() / 2);

        #trans.translate(spinner_pic.width()/2.0 , spinner_pic.height()/2.0);
        trans.rotate(angle)
        newPixmap = pixmap.transformed(QTransform().rotate(angle));
        xoffset = (newPixmap.width() - pixmap.width()) / 2;
        yoffset = (newPixmap.height() - pixmap.height()) / 2
        rotated = newPixmap.copy(xoffset, yoffset, pixmap.width(), pixmap.height());
        spinner_pic.setPixmap(rotated)
    spinnerAnim = QVariantAnimation()
    spinnerAnim.setDuration(3000)
    spinnerAnim.setStartValue(QVariant(0))
    spinnerAnim.setEndValue(QVariant(360))
    spinnerAnim.setLoopCount(-1)
    spinnerAnim.valueChanged.connect(spinnerAnimRot)
    spinner_pic.setHidden(True);

    # phone info
    phoneInfoTextbox = QLabel(w)
    phoneInfoTextbox.setText("No phone found");
    phoneInfoTextbox.setGeometry(10, 10, 520, 100);
    phoneInfoTextbox.setAlignment(Qt.AlignRight | Qt.AlignTop)
    phoneInfoTextbox.setStyleSheet("font-size: 12px;");
    phoneInfoTextbox.show();

    #Line
    line = QFrame(w)
    line.setGeometry(QRect(10, 108, 580, 20))
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)

    # logo
    pic = QLabel(w)
    pixmap = QPixmap("gui/images/logo_512.png").scaled(int(128*dpiMultiplier), int(128*dpiMultiplier), Qt.KeepAspectRatio, Qt.SmoothTransformation);
    pixmap.setDevicePixelRatio(dpiMultiplier);
    pic.setPixmap(pixmap)
    pic.resize(int(pixmap.width() / dpiMultiplier), int(pixmap.height() / dpiMultiplier))
    pic.move(10, 130);
    pic.show()

    #Copyright info
    copyrightInfo = QLabel(w)
    copyrightInfo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    copyrightInfo.setText("Made by: Bjoern Kerler\n" + \
                  "Gui by: Geert-Jan Kreileman\n\n" + \
                   "Credits: \n" + \
                   "kamakiri [xyzz]\n" +
                   "linecode exploit [chimera]\n" +
                   "Chaosmaster\n" +
                   "and all contributers");
    copyrightInfo.setGeometry(150, 135, 405, 256);
    copyrightInfo.setWordWrap(True);
    copyrightInfo.setStyleSheet("font-size: 12px; color: #333; vertical-align: top;");
    copyrightInfo.show();

    def showDebugInfo():
        logBox.show();
        if w.frameGeometry().height() < 500:
            win.setFixedSize(600, 700+addTopMargin);
            w.setFixedSize(600, 700);
            debugBtn.setText("Hide debug info")
        else:
            w.setFixedSize(600, 400);
            win.setFixedSize(600, 400+addTopMargin);
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

    win.show();

    #Get the device info
    thread = asyncThread(app, 0, getDevInfo, [mtkClass,da_handler, phoneInfo])
    thread.sendToLogSignal.connect(sendToLog);
    thread.sendUpdateSignal.connect(updateGui);
    thread.start();

    #Run loop the app
    app.exec();
    #Prevent thread from not being closed and call error end codes
    thread.terminate()
    thread.wait()
