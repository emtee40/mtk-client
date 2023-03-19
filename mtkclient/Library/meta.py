#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import time
import sys
import logging
from enum import Enum
from mtkclient.Library.utils import LogBase, logsetup

class META(metaclass=LogBase):
    class Mode(Enum):
        FASTBOOT = b"FASTBOOT"  # fastboot mode
        META = b"METAMETA"      # MAUI META mode
        EMETA = b"ADVEMETA"  # Advanced META mode
        FACT = b"FACTFACT"      # Factory menu
        ATE  = b"FACTORYM"      # ATE Signaling Test
        READY = b"READY"
        ATNBOOT = b"AT+NBOOT"

    def __init__(self, mtk, loglevel=logging.INFO):
        self.mtk = mtk
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.error = self.__logger.error
        self.gcpu = None
        self.config = mtk.config
        self.display = True
        self.rbyte = self.mtk.port.rbyte
        self.rword = self.mtk.port.rword
        self.rdword = self.mtk.port.rdword
        self.usbread = self.mtk.port.usbread
        self.usbwrite = self.mtk.port.usbwrite
        self.echo = self.mtk.port.echo
        self.sendcmd = self.mtk.port.mtk_cmd

    def init(self, metamode: bytes, maxtries=None, display=True):
        if not display:
            self.info("Status: Waiting for PreLoader VCOM, please reconnect mobile to preloader mode")
        else:
            self.info("Status: Waiting for PreLoader VCOM, please connect mobile")
        counter = 0
        loop = 0
        cdc = self.mtk.port.cdc
        while not cdc.connected:
            try:
                if maxtries is not None and counter == maxtries:
                    break
                cdc.connected = cdc.connect()
                if cdc.connected and cdc.pid == 0x2000:
                    counter += 1
                    EP_OUT = cdc.EP_OUT.write
                    EP_IN = cdc.EP_IN.read
                    maxinsize = cdc.EP_IN.wMaxPacketSize
                    while True:
                        resp=b""
                        try:
                            resp = bytearray(EP_IN(maxinsize))
                        except Exception as err:
                            break
                        if resp==b"READY":
                            EP_OUT(metamode, len(metamode))
                            while resp==b"READY":
                                resp = bytearray(EP_IN(maxinsize))
                            if resp in [b"ATEMEVDX",b"TOOBTSAF",b"ATEMATEM",b"TCAFTCAF",b"MYROTCAF"]:
                                return True
                            self.warning(resp)
                else:
                    if cdc.connected:
                        cdc.close()
                        cdc.connected = False
                    if loop == 5:
                        sys.stdout.write('\n')
                        self.info("Hint:\n\nPower off the phone before connecting.\n" + \
                                  "For preloader mode, don't press any hw button and connect usb.\n")
                        sys.stdout.write('\n')
                    if loop >= 10:
                        sys.stdout.write('.')
                    if loop >= 20:
                        sys.stdout.write('\n')
                        loop = 0
                    loop += 1
                    time.sleep(0.3)
                    sys.stdout.flush()

            except Exception as serr:
                if "access denied" in str(serr):
                    self.warning(str(serr))
                self.debug(str(serr))
                pass

        return False