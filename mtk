#!/usr/bin/env python3
# MTK Flash Client (c) B.Kerler 2018-2021.
# Licensed under MIT License
import shutil
import os
import json
import sys
import logging
import time
import argparse
from binascii import hexlify
from struct import unpack, pack
from mtkclient.config.usb_ids import default_ids
from mtkclient.config.payloads import pathconfig
from mtkclient.Library.pltools import PLTools
from mtkclient.Library.mtk_preloader import Preloader
from mtkclient.Library.mtk_daloader import DAloader
from mtkclient.Library.Port import Port
from mtkclient.Library.utils import LogBase, logsetup, getint
from mtkclient.config.brom_config import Mtk_Config
from mtkclient.Library.utils import print_progress
from mtkclient.Library.error import ErrorHandler


def split_by_n(seq, unit_count):
    """A generator to divide a sequence into chunks of n units."""
    while seq:
        yield seq[:unit_count]
        seq = seq[unit_count:]


class ArgHandler(metaclass=LogBase):
    def __init__(self, args, config):
        try:
            if args.vid is not None:
                config.vid = getint(args.vid)
        except AttributeError:
            pass
        try:
            if args.pid is not None:
                config.pid = getint(args.pid)
        except AttributeError:
            pass
        try:
            if args.payload is not None:
                config.payloadfile = args.payload
        except:
            pass
        try:
            if args.loader is not None:
                config.loader = args.loader
        except AttributeError:
            pass
        try:
            if args.da_address is not None:
                config.chipconfig.da_payload_addr = getint(args.da_address)
                self.info("O:DA offset:\t\t\t" + args.da_address)
        except AttributeError:
            pass
        try:
            if args.brom_address is not None:
                config.chipconfig.brom_payload_addr = getint(args.brom_address)
                self.info("O:Payload offset:\t\t" + args.brom_address)
        except AttributeError:
            pass
        try:
            if args.watchdog_address is not None:
                config.chipconfig.watchdog = getint(args.wdt)
                self.info("O:Watchdog addr:\t\t" + args.wdt)
        except AttributeError:
            pass
        try:
            if args.skipwdt is not None:
                config.skipwdt = args.skipwdt
        except AttributeError:
            pass
        try:
            if args.uart_address is not None:
                config.chipconfig.uart = getint(args.uart_address)
                self.info("O:Uart addr:\t\t" + args.uart_address)
        except AttributeError:
            pass
        try:
            if args.preloader is not None:
                config.chipconfig.var1 = getint(args.var1)
                self.info("O:Var1:\t\t" + args.var1)
        except AttributeError:
            pass
        try:
            if args.preloader is not None:
                config.preloader = args.preloader
        except AttributeError:
            pass
        try:
            if args.generatekeys is not None:
                config.generatekeys = args.generatekeys
        except AttributeError:
            pass
        try:
            if args.ptype is not None:
                config.ptype = args.ptype
        except AttributeError:
            pass
        try:
            if args.socid is not None:
                config.readsocid = args.socid
        except AttributeError:
            pass
        try:
            if args.crash is not None:
                config.enforcecrash = args.crash
        except AttributeError:
            pass


class Mtk(metaclass=LogBase):
    def __init__(self, config, loglevel=logging.INFO, preinit=True):
        self.config = config
        self.loader = config.loader
        self.vid = config.vid
        self.pid = config.pid
        self.interface = config.interface
        self.pathconfig = pathconfig()
        self.__logger = logsetup(self, self.__logger, loglevel)
        self.eh = ErrorHandler()
        if preinit:
            self.init()

    def patch_preloader_security(self, data):
        patched = False
        data = bytearray(data)
        patches = [
            ("A3687BB12846", "0123A3602846"),  # oppo security
            ("B3F5807F01D1", "B3F5807F01D14FF000004FF000007047"),  # confirmed : mt6739 c30, mt6833
            ("B3F5807F04BF4FF4807305F011B84FF0FF307047", "B3F5807F04BF4FF480734FF000004FF000007047"),
        ]

        i = 0
        for patchval in patches:
            pattern = bytes.fromhex(patchval[0])
            idx = data.find(pattern)
            if idx != -1:
                patch = bytes.fromhex(patchval[1])
                data[idx:idx + len(patch)] = patch
                patched = True
                # break
            i += 1
        if patched:
            # with open(sys.argv[1]+".patched","wb") as wf:
            #    wf.write(data)
            #    print("Patched !")
            self.info(f"Patched preloader security: {hex(i)}")
        else:
            self.warning(f"Failed to patch preloader security")
        return data

    def parse_preloader(self, preloader):
        if isinstance(preloader, str):
            if os.path.exists(preloader):
                with open(preloader, "rb") as rf:
                    data = rf.read()
        else:
            data = preloader
        data = bytearray(data)
        magic = unpack("<I", data[:4])[0]
        if magic == 0x014D4D4D:
            self.info(f"Valid preloader detected.")
            daaddr = unpack("<I", data[0x1C:0x20])[0]
            dasize = unpack("<I", data[0x20:0x24])[0]
            maxsize = unpack("<I", data[0x24:0x28])[0]
            content_offset = unpack("<I", data[0x28:0x2C])[0]
            sig_length = unpack("<I", data[0x2C:0x30])[0]
            jump_offset = unpack("<I", data[0x30:0x34])[0]
            daaddr = jump_offset + daaddr
            dadata = data[jump_offset:]
        else:
            self.warning("Preloader detected as shellcode, might fail to run.")
            daaddr = self.config.chipconfig.da_payload_addr
            dadata = data
        return daaddr, dadata

    def init(self, vid=None, pid=None, interface=None):
        if vid is None:
            vid = self.vid
        if pid is None:
            pid = self.pid
        if interface is None:
            interface = self.interface
        if vid != -1 and pid != -1:
            if interface == -1:
                for dev in default_ids:
                    if dev[0] == vid and dev[1] == pid:
                        interface = dev[2]
                        break
            portconfig = [[vid, pid, interface]]
        else:
            portconfig = default_ids
        self.port = Port(self, portconfig, self.__logger.level)
        self.preloader = Preloader(self, self.__logger.level)
        self.daloader = DAloader(self, self.__logger.level)

    def crasher(self, display=True, mode=None):
        rmtk = self
        plt = PLTools(self, self.__logger.level)
        if self.config.enforcecrash or self.config.meid is None:
            self.info("We're not in bootrom, trying to crash da...")
            if mode is None:
                for crashmode in range(0, 3):
                    try:
                        plt.crash(crashmode)
                    except:
                        pass
                    rmtk = Mtk(config=self.config, loglevel=self.__logger.level)
                    rmtk.preloader.display = display
                    if rmtk.preloader.init(maxtries=20):
                        break
            else:
                try:
                    plt.crash(mode)
                except Exception as err:
                    self.__logger.debug(str(err))
                    pass
                rmtk = Mtk(config=self.config, loglevel=self.__logger.level)
                rmtk.preloader.display = display
                if rmtk.preloader.init(maxtries=20):
                    return rmtk
        return rmtk

    def bypass_security(self):
        mtk = self.crasher()
        plt = PLTools(mtk, self.__logger.level)
        if self.config.payloadfile is None:
            if self.config.chipconfig.loader is None:
                self.config.payloadfile = os.path.join(self.pathconfig.get_payloads_path(),
                                                       "generic_patcher_payload.bin")
            else:
                self.config.payloadfile = os.path.join(self.pathconfig.get_payloads_path(),
                                                       self.config.chipconfig.loader)
        if plt.runpayload(filename=self.config.payloadfile):
            mtk.port.run_handshake()
            # mtk.port.close()
            # mtk = Mtk(loader=args.loader, loglevel=self.__logger.level, vid=vid, pid=pid,
            #          interface=interface, args=args)
            # mtk.preloader.init(args=args, readsocid=readsocid)
            return mtk
        else:
            self.error("Error on running kamakiri payload")
        return self


class Main(metaclass=LogBase):
    def __init__(self, args):
        self.__logger = self.__logger
        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.error = self.__logger.error
        self.warning = self.__logger.warning
        self.args = args
        if not os.path.exists("logs"):
            os.mkdir("logs")

    def dump_preloader_ram(self, mtk):
        try:
            data = b"".join([pack("<I", val) for val in mtk.preloader.read32(0x200000, 0x10000 // 4)])
            idx = data.find(b"\x4D\x4D\x4D\x01\x38\x00\x00\x00")
            if idx != -1:
                data = data[idx:]
                length = unpack("<I", data[0x20:0x24])[0]
                time.sleep(0.05)
                data = b"".join([pack("<I", val) for val in mtk.preloader.read32(0x200000 + idx, length + 4 // 4)])
                preloader = data[:length]
                idx = data.find(b"MTK_BLOADER_INFO")
                if idx != -1:
                    filename = data[idx + 0x1B:idx + 0x1B + 0x30].rstrip(b"\x00").decode('utf-8')
                    if preloader is not None:
                        pfilename = os.path.join(mtk.pathconfig.get_loader_path(), "Preloader", filename)
                        if not os.path.exists(pfilename):
                            with open(pfilename, "wb") as wf:
                                wf.write(preloader)
                                print(f"Successfully extracted preloader for this device to: {pfilename}")
                return preloader
        except Exception as err:
            self.error(str(err))
            return None

    def close(self):
        sys.exit(0)

    def run(self):
        try:
            if self.args.debugmode:
                loglevel = logging.DEBUG
                self.__logger.setLevel(logging.DEBUG)
            else:
                loglevel = logging.INFO
                self.__logger.setLevel(logging.INFO)
        except:
            loglevel = logging.INFO
            self.__logger.setLevel(logging.INFO)
            pass
        config = Mtk_Config(loglevel=loglevel)
        ArgHandler(self.args, config)
        self.eh = ErrorHandler()
        mtk = Mtk(config=config, loglevel=loglevel)
        if mtk.config.debugmode:
            logfilename = os.path.join("logs", "log.txt")
            if os.path.exists(logfilename):
                os.remove(logfilename)
            fh = logging.FileHandler(logfilename, encoding='utf-8')
            self.__logger.addHandler(fh)

        self.debug(" ".join(sys.argv))

        cmd = self.args.cmd
        if cmd == "dumpbrom":
            if mtk.preloader.init():
                rmtk = mtk.crasher()
                if rmtk is None:
                    sys.exit(0)
                if rmtk.port.cdc.vid != 0xE8D and rmtk.port.cdc.pid != 0x0003:
                    self.warning("We couldn't enter preloader.")
                filename = self.args.filename
                if filename is None:
                    cpu = ""
                    if rmtk.config.cpu != "":
                        cpu = "_" + rmtk.config.cpu
                    filename = "brom" + cpu + "_" + hex(rmtk.config.hwcode)[2:] + ".bin"
                plt = PLTools(rmtk, self.__logger.level)
                plt.run_dump_brom(filename, self.args.ptype)
                rmtk.port.close()
            self.close()
        elif cmd == "dumppreloader":
            if mtk.preloader.init():
                rmtk = mtk.crasher()
                if rmtk is None:
                    sys.exit(0)
                if rmtk.port.cdc.vid != 0xE8D and rmtk.port.cdc.pid != 0x0003:
                    self.warning("We couldn't enter preloader.")
                plt = PLTools(rmtk, self.__logger.level)
                data, filename = plt.run_dump_preloader(self.args.ptype)
                if data is not None:
                    if filename == "":
                        if self.args.filename is not None:
                            filename = self.args.filename
                        else:
                            filename = "preloader.bin"
                    with open(filename, 'wb') as wf:
                        print_progress(0, 100, prefix='Progress:', suffix='Complete', bar_length=50)
                        wf.write(data)
                        print_progress(100, 100, prefix='Progress:', suffix='Complete', bar_length=50)
                        self.info("Preloader dumped as: " + filename)
                rmtk.port.close()
            self.close()
        elif cmd == "brute":
            self.info("Kamakiri / DA Bruteforce run")
            rmtk = Mtk(config=mtk.config, loglevel=self.__logger.level)
            plt = PLTools(rmtk, self.__logger.level)
            plt.runbrute(self.args)
            self.close()
        elif cmd == "crash":
            if mtk.preloader.init():
                mtk = mtk.crasher(mode=getint(self.args.mode))
            mtk.port.close()
            self.close()
        elif cmd == "plstage":
            dadata = None
            if mtk.config.chipconfig.pl_payload_addr is not None:
                plstageaddr = mtk.config.chipconfig.pl_payload_addr
            else:
                plstageaddr = 0x40200000  # 0x40001000
            if self.args.pl is None:
                plstage = os.path.join(mtk.pathconfig.get_payloads_path(), "pl.bin")
            else:
                plstage = self.args.pl
            if os.path.exists(plstage):
                with open(plstage, "rb") as rf:
                    rf.seek(0)
                    pldata = rf.read()
            if mtk.preloader.init():
                if mtk.config.target_config["daa"]:
                    mtk = mtk.bypass_security()
                    if mtk is None:
                        self.error("Error on bypassing security, aborting")
                        return
                self.info("Connected to device, loading")
            else:
                self.error("Couldn't connect to device, aborting.")
            if mtk.config.preloader is not None:
                filename = mtk.config.preloader
            if mtk.config.is_brom and mtk.config.preloader is None:
                self.warning("PL stage needs preloader, please use --preloader option. " +
                             "Trying to dump preloader from ram.")
                plt = PLTools(mtk=mtk, loglevel=self.__logger.level)
                dadata, filename = plt.run_dump_preloader(self.args.ptype)
                mtk.config.preloader = mtk.patch_preloader_security(dadata)
            if mtk.config.preloader is not None:
                self.info("Using custom preloader : " + filename)
                daaddr, dadata = mtk.parse_preloader(mtk.config.preloader)
                mtk.config.preloader = mtk.patch_preloader_security(dadata)
                if mtk.preloader.send_da(daaddr, len(dadata), 0x100, dadata):
                    self.info(f"Sent preloader to {hex(daaddr)}, length {hex(len(dadata))}")
                    if mtk.preloader.jump_da(daaddr):
                        self.info(f"PL Jumped to daaddr {hex(daaddr)}.")
                        time.sleep(2)
                        sys.exit(1)
                        mtk = Mtk(config=mtk.config, loglevel=self.__logger.level)
                        res = mtk.preloader.init()
                        if not res:
                            self.error("Error on loading preloader")
                            return
                        else:
                            self.info("Successfully connected to pl")

                        if self.args.startpartition is not None:
                            partition = self.args.startpartition
                            self.info("Booting to : " + partition)
                            # if data[0:4]!=b"\x88\x16\x88\x58":
                            #    data=0x200*b"\x00"+data
                            mtk.preloader.send_partition_data(partition, pldata)
                            status = mtk.preloader.jump_to_partition(partition)  # Do not remove !
                            res = mtk.preloader.read32(0x10C180, 10)
                            for val in res:
                                print(hex(val))
                            if status != 0x0:
                                self.error("Error on jumping to partition: " + self.eh.status(status))
                            else:
                                self.info("Jumping to partition ....")
                            return
            if mtk.preloader.send_da(plstageaddr, len(pldata), 0x100, pldata):
                self.info(f"Sent stage2 to {hex(plstageaddr)}, length {hex(len(pldata))}")
                mtk.preloader.get_hw_sw_ver()
                if mtk.preloader.jump_da(plstageaddr):
                    self.info(f"Jumped to stage2 at {hex(plstageaddr)}.")
                    ack = unpack(">I", mtk.port.usbread(4))[0]
                    if ack == 0xB1B2B3B4:
                        self.info("Successfully loaded stage2")
                        return
                else:
                    self.error("Error on jumping to pl")
                    return
            else:
                self.error("Error on sending pl")
                return
            self.close()
        elif cmd == "peek":
            addr = getint(self.args.address)
            length = getint(self.args.length)
            if self.args.preloader is not None:
                preloader = self.args.preloader
                if os.path.exists(preloader):
                    daaddr, dadata = mtk.parse_preloader(preloader)
            if self.args.filename is None:
                filename = ""
            else:
                filename = self.args.filename
            if mtk.preloader.init():
                if mtk.config.target_config["daa"]:
                    mtk = mtk.bypass_security()
            if mtk is not None:
                if self.args.preloader is not None:
                    if mtk.preloader.send_da(daaddr, len(dadata), 0x100, dadata):
                        self.info(f"Sent preloader to {hex(daaddr)}, length {hex(len(dadata))}")
                        if mtk.preloader.jump_da(daaddr):
                            self.info(f"Jumped to pl {hex(daaddr)}.")
                            time.sleep(2)
                            mtk = Mtk(loglevel=self.__logger.level)
                            res = mtk.preloader.init()
                            if not res:
                                self.error("Error on loading preloader")
                                return
                            else:
                                self.info("Successfully connected to pl.")
                                # mtk.preloader.get_hw_sw_ver()
                                # status=mtk.preloader.jump_to_partition(b"") # Do not remove !
                    else:
                        self.error("Error on jumping to pl")
                        return
                self.info("Starting to read ...")
                dwords = length // 4
                if length % 4:
                    dwords += 1
                if filename != "":
                    wf = open(filename, "wb")
                sdata = b""
                print_progress(0, 100, prefix='Progress:',
                               suffix='Starting, addr 0x%08X' % addr, bar_length=50)
                length = dwords * 4
                old = 0
                pos = 0
                while dwords:
                    size = min(512 // 4, dwords)
                    data = b"".join(int.to_bytes(val, 4, 'little') for val in mtk.preloader.read32(addr + pos, size))
                    sdata += data
                    if filename != "":
                        wf.write(data)
                    pos += len(data)
                    prog = pos / length * 100
                    if round(prog, 1) > old:
                        print_progress(prog, 100, prefix='Progress:',
                                       suffix='Complete, addr 0x%08X' % (addr + pos), bar_length=50)
                        old = round(prog, 1)
                    dwords = (length - pos) // 4
                print_progress(100, 100, prefix='Progress:',
                               suffix='Finished', bar_length=50)
                if filename == "":
                    print(hexlify(sdata).decode('utf-8'))
                else:
                    wf.close()
                    self.info(f"Data from {hex(addr)} with size of {hex(length)} was written to " + filename)
            self.close()
        elif cmd == "stage":
            if self.args.filename is None:
                pc = pathconfig()
                stage1file = os.path.join(pc.get_payloads_path(), "generic_stage1_payload.bin")
            else:
                stage1file = self.args.filename
            if not os.path.exists(stage1file):
                self.error(f"Error: {stage1file} doesn't exist !")
                return False
            if self.args.stage2addr is None:
                stage2addr = None
            else:
                stage2addr = getint(self.args.stage2addr)
            if self.args.stage2 is None:
                stage2file = os.path.join(mtk.pathconfig.get_payloads_path(), "stage2.bin")
            else:
                stage2file = self.args.stage2
                if not os.path.exists(stage2file):
                    self.error(f"Error: {stage2file} doesn't exist !")
                    return False
            verifystage2 = self.args.verifystage2
            if mtk.preloader.init():
                mtk = mtk.crasher()
                if mtk.port.cdc.pid == 0x0003:
                    plt = PLTools(mtk, self.__logger.level)
                    self.info("Uploading stage 1")
                    if plt.runpayload(filename=stage1file):
                        self.info("Successfully uploaded stage 1, sending stage 2")
                        with open(stage2file, "rb") as rr:
                            stage2data = rr.read()
                            while len(stage2data) % 0x200:
                                stage2data += b"\x00"
                        if stage2addr is None:
                            stage2addr = mtk.config.chipconfig.da_payload_addr
                            if stage2addr is None:
                                stage2addr = 0x201000

                        # ###### Send stage2
                        # magic
                        mtk.port.usbwrite(pack(">I", 0xf00dd00d))
                        # cmd write
                        mtk.port.usbwrite(pack(">I", 0x4000))
                        # address
                        mtk.port.usbwrite(pack(">I", stage2addr))
                        # length
                        mtk.port.usbwrite(pack(">I", len(stage2data)))
                        bytestowrite = len(stage2data)
                        pos = 0
                        while bytestowrite > 0:
                            size = min(bytestowrite, 1)
                            if mtk.port.usbwrite(stage2data[pos:pos + size]):
                                bytestowrite -= size
                                pos += size
                        # mtk.port.usbwrite(b"")
                        time.sleep(0.1)
                        flag = mtk.port.rdword()
                        if flag != 0xD0D0D0D0:
                            self.error(f"Error on sending stage2, size {hex(len(stage2data))}.")
                        self.info(f"Done sending stage2, size {hex(len(stage2data))}.")

                        if verifystage2:
                            self.info("Verifying stage2 data")
                            rdata = b""
                            mtk.port.usbwrite(pack(">I", 0xf00dd00d))
                            mtk.port.usbwrite(pack(">I", 0x4002))
                            mtk.port.usbwrite(pack(">I", stage2addr))
                            mtk.port.usbwrite(pack(">I", len(stage2data)))
                            bytestoread = len(stage2data)
                            while bytestoread > 0:
                                size = min(bytestoread, 1)
                                rdata += mtk.port.usbread(size)
                                bytestoread -= size
                            flag = mtk.port.rdword()
                            if flag != 0xD0D0D0D0:
                                self.error("Error on reading stage2 data")
                            if rdata != stage2data:
                                self.error("Stage2 data doesn't match")
                                with open("rdata", "wb") as wf:
                                    wf.write(rdata)
                            else:
                                self.info("Stage2 verification passed.")

                        # ####### Kick Watchdog
                        # magic
                        # mtk.port.usbwrite(pack("<I", 0xf00dd00d))
                        # cmd kick_watchdog
                        # mtk.port.usbwrite(pack("<I", 0x3001))

                        # ######### Jump stage1
                        # magic
                        mtk.port.usbwrite(pack(">I", 0xf00dd00d))
                        # cmd jump
                        mtk.port.usbwrite(pack(">I", 0x4001))
                        # address
                        mtk.port.usbwrite(pack(">I", stage2addr))
                        self.info("Done jumping stage2 at %08X" % stage2addr)
                        ack = unpack(">I", mtk.port.usbread(4))[0]
                        if ack == 0xB1B2B3B4:
                            self.info("Successfully loaded stage2")
                self.close()
            else:
                mtk.port.close()
                return False
        elif cmd == "payload":
            if mtk.preloader.init():
                mtk = mtk.crasher()
                plt = PLTools(mtk, self.__logger.level)
                payloadfile = self.args.payload
                if payloadfile is None:
                    if mtk.config.chipconfig.loader is None:
                        payloadfile = os.path.join(mtk.pathconfig.get_payloads_path(), "generic_patcher_payload.bin")
                    else:
                        payloadfile = os.path.join(mtk.pathconfig.get_payloads_path(), mtk.config.chipconfig.loader)
                ptype = ""
                if self.args.ptype is not None:
                    ptype = self.args.ptype
                plt.runpayload(filename=payloadfile)
            mtk.port.close(reset=True)
            self.close()
        elif cmd == "gettargetconfig":
            if mtk.preloader.init():
                self.info("Getting target info...")
                mtk.preloader.get_target_config()
            mtk.port.close()
            self.close()
        else:
            # DA / FLash commands start here

            mtk.port.cdc.connected = mtk.port.cdc.connect()
            if mtk.port.cdc.connected and os.path.exists(".state"):
                info = mtk.daloader.reinit()
            else:
                try:
                    preloader = self.args.preloader
                except:
                    preloader = None
                if mtk.preloader.init():
                    if mtk.config.target_config["daa"]:
                        mtk = mtk.bypass_security()
                        self.info("Device is protected.")
                        if mtk is not None:
                            if mtk.config.is_brom:
                                self.info("Device is in BROM mode. Trying to dump preloader.")
                                if preloader is None:
                                    preloader = self.dump_preloader_ram(mtk)
                    else:
                        self.info("Device is unprotected.")
                        if mtk.config.is_brom:
                            mtk = mtk.bypass_security()  # Needed for dumping preloader
                            if preloader is None:
                                self.warning(
                                    "Device is in BROM mode. No preloader given, trying to dump preloader from ram.")
                                preloader = self.dump_preloader_ram(mtk)
                                if preloader is None:
                                    self.error("Failed to dump preloader from ram.")
                    if not mtk.daloader.upload_da(preloader=preloader):
                        self.error("Error uploading da")
                        return False
                    else:
                        mtk.daloader.writestate()
                else:
                    return False

            if cmd == "gpt":
                directory = self.args.directory
                if directory is None:
                    directory = ""

                sfilename = os.path.join(directory, f"gpt_main.bin")
                data, guid_gpt = mtk.daloader.get_gpt(self.args)
                if guid_gpt is None:
                    self.error("Error reading gpt")
                    self.close()
                else:
                    with open(sfilename, "wb") as wf:
                        wf.write(data)

                    print(f"Dumped GPT from to {sfilename}")
                    sfilename = os.path.join(directory, f"gpt_backup.bin")
                    with open(sfilename, "wb") as wf:
                        wf.write(data[mtk.daloader.daconfig.pagesize:])
                    print(f"Dumped Backup GPT to {sfilename}")
                self.close()
            elif cmd == "printgpt":
                data, guid_gpt = mtk.daloader.get_gpt(self.args)
                if guid_gpt is None:
                    self.error("Error reading gpt")
                else:
                    guid_gpt.print()
                self.close()
            elif cmd == "r":
                partitionname = self.args.partitionname
                parttype = self.args.parttype
                filename = self.args.filename
                filenames = filename.split(",")
                partitions = partitionname.split(",")
                if len(partitions) != len(filenames):
                    self.error("You need to gives as many filenames as given partitions.")
                    self.close()
                if parttype == "user" or parttype is None:
                    i = 0
                    countDump = 0
                    self.info("Requesting available partitions ....")
                    gpttable = mtk.daloader.get_partition_data(self.args, parttype=parttype)
                    for partition in partitions:
                        partfilename = filenames[i]
                        i += 1
                        if partition == "gpt":
                            mtk.daloader.readflash(addr=0,
                                                   length=0x16000,
                                                   filename=partfilename, parttype=parttype)
                            continue
                        else:
                            rpartition = None
                            for gptentry in gpttable:
                                if gptentry.name.lower() == partition.lower():
                                    rpartition = gptentry
                                    break
                            if rpartition is not None:
                                self.info(f"Dumping partition \"{rpartition.name}\"")
                                if mtk.daloader.readflash(addr=rpartition.sector * mtk.daloader.daconfig.pagesize,
                                                          length=rpartition.sectors * mtk.daloader.daconfig.pagesize,
                                                          filename=partfilename, parttype=parttype):
                                    self.info(f"Dumped sector {str(rpartition.sector)} with sector count " +
                                              f"{str(rpartition.sectors)} as {partfilename}.")
                                    countDump += 1
                                else:
                                    self.info(f"Failed to dump sector {str(rpartition.sector)} with sector count " +
                                              f"{str(rpartition.sectors)} as {partfilename}.")
                                    countDump += 1
                            else:
                                self.error(f"Error: Couldn't detect partition: {partition}\nAvailable partitions:")
                                for rpartition in gpttable:
                                    self.info(rpartition.name)
                    if countDump > 1 and countDump == len(filenames):
                        self.info(f"All partitions were dumped")
                    elif countDump > 1 and countDump != len(filenames):
                        self.info(f"Failed to dump some partitions")
                else:
                    i = 0
                    for partfilename in filenames:
                        pos = 0
                        if mtk.daloader.readflash(addr=pos, length=0xFFFFFFFF, filename=partfilename,
                                                  parttype=parttype):
                            print(f"Dumped partition {str(partitionname)} as {partfilename}.")
                        else:
                            print(f"Failed to dump partition {str(partitionname)} as {partfilename}.")
                        i += 1
                self.close()
            elif cmd == "rl":
                directory = self.args.directory
                parttype = self.args.parttype
                if self.args.skip:
                    skip = self.args.skip.split(",")
                else:
                    skip = []
                if not os.path.exists(directory):
                    os.mkdir(directory)
                data, guid_gpt = mtk.daloader.get_gpt(self.args, parttype=parttype)
                if guid_gpt is None:
                    self.error("Error reading gpt")
                else:
                    storedir = directory
                    if not os.path.exists(storedir):
                        os.mkdir(storedir)
                    sfilename = os.path.join(storedir, f"gpt_main.bin")
                    with open(sfilename, "wb") as wf:
                        wf.write(data)

                    sfilename = os.path.join(storedir, f"gpt_backup.bin")
                    with open(sfilename, "wb") as wf:
                        wf.write(data[mtk.daloader.daconfig.pagesize * 2:])

                    countGPT = 0
                    for partition in guid_gpt.partentries:
                        partitionname = partition.name
                        if partition.name in skip:
                            continue
                        filename = os.path.join(storedir, partitionname + ".bin")
                        self.info(
                            f"Dumping partition {str(partition.name)} with sector count {str(partition.sectors)} " +
                            f"as {filename}.")

                        if mtk.daloader.readflash(addr=partition.sector * mtk.daloader.daconfig.pagesize,
                                                  length=partition.sectors * mtk.daloader.daconfig.pagesize,
                                                  filename=filename,
                                                  parttype=parttype):

                            countGPT += 1
                            self.info(f"Dumped partition {str(partition.name)} as {str(filename)}.")
                        else:
                            countGPT -= 1
                            self.error(f"Failed to dump partition {str(partition.name)} as {str(filename)}.")

                    partitionsForRead = len(guid_gpt.partentries) - len(skip)
                    if countGPT == partitionsForRead:
                        self.info(f"All Dumped partitions success.")
                    else:
                        self.error(f"Failed to dump all partitions")
                self.close()
            elif cmd == "rf":
                filename = self.args.filename
                parttype = self.args.parttype
                if mtk.daloader.daconfig.flashtype == "ufs":
                    if parttype == "lu0":
                        length = mtk.daloader.daconfig.flashsize[0]
                    elif parttype == "lu1":
                        length = mtk.daloader.daconfig.flashsize[1]
                    elif parttype == "lu2":
                        length = mtk.daloader.daconfig.flashsize[2]
                    else:
                        length = mtk.daloader.daconfig.flashsize[0]
                else:
                    length = mtk.daloader.daconfig.flashsize
                print(f"Dumping sector 0 with flash size {hex(length)} as {filename}.")
                if mtk.daloader.readflash(addr=0, length=length, filename=filename, parttype=parttype):
                    print(f"Dumped sector 0 with flash size {hex(length)} as {filename}.")
                else:
                    print(f"Failed to dump sector 0 with flash size {hex(length)} as {filename}.")
                self.close()
            elif cmd == "rs":
                start = getint(self.args.startsector)
                sectors = getint(self.args.sectors)
                filename = self.args.filename
                parttype = self.args.parttype
                if mtk.daloader.readflash(addr=start * mtk.daloader.daconfig.pagesize,
                                          length=sectors * mtk.daloader.daconfig.pagesize,
                                          filename=filename, parttype=parttype):
                    print(f"Dumped sector {str(start)} with sector count {str(sectors)} as {filename}.")
                else:
                    print(f"Failed to dump sector {str(start)} with sector count {str(sectors)} as {filename}.")
                self.close()
            elif cmd == "ro":
                start = getint(self.args.offset)
                length = getint(self.args.length)
                filename = self.args.filename
                parttype = self.args.parttype
                if mtk.daloader.readflash(addr=start,
                                          length=length,
                                          filename=filename, parttype=parttype):
                    print(f"Dumped offset {hex(start)} with length {hex(length)} as {filename}.")
                else:
                    print(f"Failed to dump offset {hex(start)} with length {hex(length)} as {filename}.")
                self.close()
            elif cmd == "footer":
                filename = self.args.filename
                data, guid_gpt = mtk.daloader.get_gpt(self.args)
                if guid_gpt is None:
                    self.error("Error reading gpt")
                    self.close()
                else:
                    pnames = ["userdata2", "metadata", "userdata", "reserved1", "reserved2", "reserved3"]
                    for partition in guid_gpt.partentries:
                        if partition.name in pnames:
                            print(f"Detected partition: {partition.name}")
                            if partition.name in ["userdata2", "userdata"]:
                                data = mtk.daloader.readflash(
                                    addr=(partition.sector + partition.sectors) *
                                         mtk.daloader.daconfig.pagesize - 0x4000,
                                    length=0x4000, filename="", parttype="user", display=False)
                            else:
                                data = mtk.daloader.readflash(addr=partition.sector * mtk.daloader.daconfig.pagesize,
                                                              length=0x4000, filename="", parttype="user",
                                                              display=False)
                            if data == b"":
                                continue
                            val = unpack("<I", data[:4])[0]
                            if (val & 0xFFFFFFF0) == 0xD0B5B1C0:
                                with open(filename, "wb") as wf:
                                    wf.write(data)
                                    print(f"Dumped footer from {partition.name} as {filename}.")
                                    self.close()
                                    return
                self.error(f"Error: Couldn't detect footer partition.")
                self.close()
            elif cmd == "w":
                partitionname = self.args.partitionname
                filename = self.args.filename
                parttype = self.args.parttype
                filenames = filename.split(",")
                partitions = partitionname.split(",")
                if len(partitions) != len(filenames):
                    self.error("You need to gives as many filenames as given partitions.")
                    self.close()
                    exit(0)
                if parttype == "user" or parttype is None:
                    i = 0
                    for partition in partitions:
                        partfilename = filenames[i]
                        i += 1
                        if partition == "gpt":
                            mtk.daloader.writeflash(addr=0,
                                                    length=os.stat(partfilename).st_size,
                                                    filename=partfilename,
                                                    parttype=parttype)
                            continue
                        res = mtk.daloader.detect_partition(self.args, partition, parttype)
                        if res[0]:
                            rpartition = res[1]
                            if mtk.daloader.writeflash(addr=rpartition.sector * mtk.daloader.daconfig.pagesize,
                                                       length=rpartition.sectors * mtk.daloader.daconfig.pagesize,
                                                       filename=partfilename,
                                                       parttype=parttype):
                                print(
                                    f"Wrote {partfilename} to sector {str(rpartition.sector)} with " +
                                    f"sector count {str(rpartition.sectors)}.")
                            else:
                                print(
                                    f"Failed to write {partfilename} to sector {str(rpartition.sector)} with " +
                                    f"sector count {str(rpartition.sectors)}.")
                        else:
                            self.error(f"Error: Couldn't detect partition: {partition}\nAvailable partitions:")
                            for rpartition in res[1]:
                                self.info(rpartition.name)
                else:
                    pos = 0
                    for partfilename in filenames:
                        size = os.stat(partfilename).st_size
                        if mtk.daloader.writeflash(addr=pos, length=size, filename=partfilename,
                                                   parttype=parttype):
                            print(f"Wrote {partfilename} to sector {str(pos // 0x200)} with " +
                                  f"sector count {str(size)}.")
                        else:
                            print(f"Failed to write {partfilename} to sector {str(pos // 0x200)} with " +
                                  f"sector count {str(size)}.")
                        psize = size // 0x200 * 0x200
                        if size % 0x200 != 0:
                            psize += 0x200
                        pos += psize
                self.close()
            elif cmd == "wl":
                directory = self.args.directory
                parttype = self.args.parttype
                filenames = []
                for dirName, subdirList, fileList in os.walk(directory):
                    for fname in fileList:
                        filenames.append(os.path.join(dirName, fname))

                if parttype == "user" or parttype is None:
                    i = 0
                    for partfilename in filenames:
                        partition = os.path.basename(partfilename)
                        partition = os.path.splitext(partition)[0]
                        i += 1
                        if partition == "gpt":
                            self.info(f"Writing partition {partition}")
                            if mtk.daloader.writeflash(addr=0,
                                                       length=os.stat(partfilename).st_size,
                                                       filename=partfilename,
                                                       parttype=parttype):
                                print(f"Wrote {partition} to sector {str(0)}")
                            else:
                                print(f"Failed to write {partition} to sector {str(0)}")
                            continue
                        res = mtk.daloader.detect_partition(self.args, partition, parttype)
                        if res[0]:
                            rpartition = res[1]
                            if mtk.daloader.writeflash(addr=rpartition.sector * mtk.daloader.daconfig.pagesize,
                                                       length=rpartition.sectors * mtk.daloader.daconfig.pagesize,
                                                       filename=partfilename,
                                                       parttype=parttype):
                                print(
                                    f"Wrote {partfilename} to sector {str(rpartition.sector)} with " +
                                    f"sector count {str(rpartition.sectors)}.")
                            else:
                                print(
                                    f"Failed to write {partfilename} to sector {str(rpartition.sector)} with " +
                                    f"sector count {str(rpartition.sectors)}.")
                        else:
                            self.error(f"Error: Couldn't detect partition: {partition}\n, skipping")
                else:
                    pos = 0
                    for partfilename in filenames:
                        size = os.stat(partfilename).st_size
                        partition = os.path.basename(partfilename)
                        partition = os.path.splitext(partition)[0]
                        self.info(f"Writing filename {partfilename}")
                        if mtk.daloader.writeflash(addr=pos, length=size, filename=partfilename,
                                                   partitionname=partition,
                                                   parttype=parttype):
                            print(f"Wrote {partfilename} to sector {str(pos // 0x200)} with " +
                                  f"sector count {str(size)}.")
                        else:
                            print(f"Failed to write {partfilename} to sector {str(pos // 0x200)} with " +
                                  f"sector count {str(size)}.")
                        psize = size // 0x200 * 0x200
                        if size % 0x200 != 0:
                            psize += 0x200
                        pos += psize
                self.close()
            elif cmd == "wo":
                start = getint(self.args.offset)
                length = getint(self.args.length)
                filename = self.args.filename
                parttype = self.args.parttype
                if filename is None:
                    self.error("No filename given to write to flash")
                    self.close()
                    return
                if not os.path.exists(filename):
                    self.error(f"Filename {filename} to write doesn't exist")
                    self.close()
                    return
                self.info(f"Writing offset {hex(start)} with length {hex(length)}")
                if mtk.daloader.writeflash(addr=start,
                                           length=length,
                                           filename=filename,
                                           parttype=parttype):
                    print(f"Wrote {filename} to offset {hex(start)} with " + \
                          f"length {hex(length)}.")
                else:
                    print(f"Failed to write {filename} to offset {hex(start)} with " + \
                          f"length {hex(length)}.")
                self.close()
            elif cmd == "e":
                partitionname = self.args.partitionname
                parttype = self.args.parttype
                partitions = partitionname.split(",")
                if parttype == "user" or parttype is None:
                    countFP = 0
                    i = 0
                    for partition in partitions:
                        i += 1
                        res = mtk.daloader.detect_partition(self.args, partition, parttype)
                        if res[0]:
                            rpartition = res[1]
                            if mtk.daloader.formatflash(addr=rpartition.sector * mtk.daloader.daconfig.pagesize,
                                                        length=rpartition.sectors * mtk.daloader.daconfig.pagesize,
                                                        partitionname=partition, parttype=parttype):
                                print(
                                    f"Formatted sector {str(rpartition.sector)} with " +
                                    f"sector count {str(rpartition.sectors)}.")
                                countFP += 1
                            else:
                                print(
                                    f"Failed to format sector {str(rpartition.sector)} with " +
                                    f"sector count {str(rpartition.sectors)}.")
                                countFP -= 1
                        else:
                            self.error(f"Error: Couldn't detect partition: {partition}\nAvailable partitions:")
                            for rpartition in res[1]:
                                self.info(rpartition.name)
                if (countFP == len(partitions) and countFP > 1):
                    print(f"All partitions formatted.")
                elif (countFP != len(partitions) and countFP > 1):
                    print(f"Failed to format all partitions.")
                self.close()
            elif cmd == "es":
                partitionname = self.args.partitionname
                parttype = self.args.parttype
                sectors = getint(self.args.sectors)
                if self.args.sectors is None:
                    self.error("Sector count is missing. Usage: es [partname] [sector count]")
                    self.close()
                partitions = partitionname.split(",")
                if parttype == "user" or parttype is None:
                    i = 0
                    for partition in partitions:
                        i += 1
                        res = mtk.daloader.detect_partition(self.args, partition, parttype)
                        if res[0]:
                            rpartition = res[1]
                            rsectors = min(sectors * mtk.daloader.daconfig.pagesize,
                                           rpartition.sectors * mtk.daloader.daconfig.pagesize)
                            if sectors > rsectors:
                                self.error(f"Partition {partition} only has {rsectors}, you were using {sectors}. " +
                                           f"Aborting")
                                continue
                            wipedata = b"\x00" * 0x200000
                            error = False
                            sector = rpartition.sector
                            while sectors:
                                sectorsize = sectors * mtk.daloader.daconfig.pagesize
                                wsize = min(sectorsize, 0x200000)
                                if mtk.daloader.writeflash(addr=sector * mtk.daloader.daconfig.pagesize,
                                                           length=wsize,
                                                           filename=None,
                                                           wdata=wipedata[:wsize],
                                                           parttype=parttype):
                                    print(
                                        f"Failed to format sector {str(sector)} with " +
                                        f"sector count {str(sectors)}.")
                                    error = True
                                    break
                                sectors -= (wsize // mtk.daloader.daconfig.pagesize)
                                sector += (wsize // mtk.daloader.daconfig.pagesize)
                            if not error:
                                print(
                                    f"Formatted sector {str(rpartition.sector)} with " +
                                    f"sector count {str(sectors)}.")
                        else:
                            self.error(f"Error: Couldn't detect partition: {partition}\nAvailable partitions:")
                            for rpartition in res[1]:
                                self.info(rpartition.name)
                else:
                    pos = 0
                    for partitionname in partitions:
                        mtk.daloader.formatflash(addr=pos, length=0xF000000, partitionname=partitionname,
                                                 parttype=parttype,
                                                 display=True)
                        print(f"Formatted sector {str(pos // 0x200)}")
                self.close()
            elif cmd == "wf":
                filename = self.args.filename
                parttype = self.args.parttype
                filenames = filename.split(",")
                pos = 0
                for partfilename in filenames:
                    size = os.stat(partfilename).st_size // 0x200 * 0x200
                    if mtk.daloader.writeflash(addr=pos,
                                               length=size,
                                               filename=partfilename,
                                               parttype=parttype):
                        print(f"Wrote {partfilename} to sector {str(pos // 0x200)} with " +
                              f"sector count {str(size // 0x200)}.")
                    else:
                        print(f"Failed to write {partfilename} to sector {str(pos // 0x200)} with " +
                              f"sector count {str(size // 0x200)}.")
                self.close()
            elif cmd == "reset":
                if os.path.exists(".state"):
                    os.remove(".state")
                mtk.daloader.close()
                self.close()
                print("Reset command was sent. Disconnect usb cable to power off.")
            elif cmd == "xflash":
                subcmd = args.subcmd
                if subcmd is None:
                    print("Available xflash cmds are: [peek, poke, generatekeys, seccfg, rpmb]")
                    return
                if subcmd == "peek":
                    addr = getint(self.args.address)
                    length = getint(self.args.length)
                    data = mtk.daloader.peek(addr=addr, length=length)
                    if data != b"":
                        if self.args.filename is not None:
                            filename = self.args.filename
                            open(filename, "wb").write(data)
                            self.info(f"Successfully wrote data from {hex(addr)}, length {hex(length)} to {filename}")
                        else:
                            self.info(
                                f"Data read from {hex(addr)}, length: {hex(length)}:\n{hexlify(data).decode('utf-8')}\n")
                elif subcmd == "poke":
                    addr = getint(self.args.address)
                    if self.args.filename is not None:
                        if os.path.exists(self.args.filename):
                            data = open(self.args.filename, "rb").read()
                    else:
                        if "0x" in self.args.data:
                            data = pack("<I", int(self.args.data, 16))
                        else:
                            data = bytes.fromhex(self.args.data)
                    if mtk.daloader.poke(addr=addr, data=data):
                        self.info(f"Successfully wrote data to {hex(addr)}, length {hex(len(data))}")
                elif subcmd == "generatekeys":
                    mtk.daloader.keys()
                elif subcmd == "seccfg":
                    mtk.daloader.seccfg(args.flag)
                elif subcmd == "rpmb":
                    rpmb_subcmd = args.rpmb_subcmd
                    if rpmb_subcmd is None:
                        print('Available xflash rpmb cmds are: [r w]')
                    if rpmb_subcmd == "r":
                        mtk.daloader.read_rpmb(args.filename)
                    elif rpmb_subcmd == "w":
                        mtk.daloader.write_rpmb(args.filename)
                self.close()


info = "MTK Flash/Exploit Client V1.52 (c) B.Kerler 2018-2021"

cmds = {
    "printgpt": "Print GPT Table information",
    "gpt": "Save gpt table to given directory",
    "r": "Read flash to filename",
    "rl": "Read all partitions from flash to a directory",
    "rf": "Read whole flash to file",
    "rs": "Read sectors starting at start_sector to filename",
    "ro": "Read flash starting at offset to filename",
    "w": "Write partition from filename",
    "wf": "Write flash from filename",
    "wl": "Write partitions from directory path to flash",
    "wo": "Write flash starting at offset from filename",
    "e": "Erase partition",
    "es": "Erase partition with sector count",
    "footer": "Read crypto footer from flash",
    "reset": "Send mtk reset command",
    "dumpbrom": "Try to dump the bootrom",
    "dumppreloader": "Try to dump the preloader",
    "payload": "Run a specific kamakiri / da payload, if no filename is given, generic patcher is used",
    "crash": "Try to crash the preloader",
    "brute": "Bruteforce the kamakiri var1",
    "gettargetconfig": "Get target config (sbc, daa, etc.)",
    "peek": "Read memory in patched preloader mode",
    "stage": "Run stage2 payload via boot rom mode (kamakiri)",
    "plstage": "Run stage2 payload via preloader mode (send_da)",
    "xflash": "Run da xflash special commands"
}


def showcommands():
    print(info)
    print("-----------------------------------\n")
    print("Available commands are:\n")
    for cmd in cmds:
        print("%20s" % (cmd) + ":\t" + cmds[cmd])
    print()


if __name__ == '__main__':
    print(info)
    print("")
    parser = argparse.ArgumentParser(description=info)
    subparsers = parser.add_subparsers(dest="cmd",
                                       help='Valid commands are: \n' +
                                            'printgpt, gpt, r, rl, rf, rs, w, wf, wl, e, es, footer, reset, \n' +
                                            'dumpbrom, dumppreloader, payload, crash, brute, gettargetconfig, \n' +
                                            'peek, stage, plstage, da \n')

    parser_printgpt = subparsers.add_parser("printgpt", help="Print GPT Table information")
    parser_gpt = subparsers.add_parser("gpt", help="Save gpt table to given directory")
    parser_r = subparsers.add_parser("r", help="Read flash to filename")
    parser_rl = subparsers.add_parser("rl", help="Read all partitions from flash to a directory")
    parser_rf = subparsers.add_parser("rf", help="Read whole flash to file")
    parser_rs = subparsers.add_parser("rs", help="Read sectors starting at start_sector to filename")
    parser_ro = subparsers.add_parser("ro", help="Read flash starting at offset to filename")
    parser_w = subparsers.add_parser("w", help="Write partition from filename")
    parser_wf = subparsers.add_parser("wf", help="Write flash from filename")
    parser_wl = subparsers.add_parser("wl", help="Write partitions from directory path to flash")
    parser_wo = subparsers.add_parser("wo", help="Write flash starting at offset from filename")
    parser_e = subparsers.add_parser("e", help="Erase partition")
    parser_es = subparsers.add_parser("es", help="Erase partition with sector count")
    parser_footer = subparsers.add_parser("footer", help="Read crypto footer from flash")

    parser_reset = subparsers.add_parser("reset", help="Send mtk reset command")
    parser_dumpbrom = subparsers.add_parser("dumpbrom", help="Try to dump the bootrom")
    parser_dumppreloader = subparsers.add_parser("dumppreloader", help="Try to dump the preloader")
    parser_payload = subparsers.add_parser("payload",
                                           help="Run a specific kamakiri / da payload, " +
                                                "if no filename is given, generic patcher is used")
    parser_crash = subparsers.add_parser("crash", help="Try to crash the preloader")
    parser_brute = subparsers.add_parser("brute", help="Bruteforce the kamakiri var1")
    parser_gettargetconfig = subparsers.add_parser("gettargetconfig", help="Get target config (sbc, daa, etc.)")
    parser_peek = subparsers.add_parser("peek", help="Read memory in patched preloader mode")
    parser_stage = subparsers.add_parser("stage", help="Run stage2 payload via boot rom mode (kamakiri)")
    parser_plstage = subparsers.add_parser("plstage", help="Run stage2 payload via preloader mode (send_da)")

    parser_xflash = subparsers.add_parser("xflash", help="Run xflash special commands")
    da_cmds = parser_xflash.add_subparsers(dest='subcmd', help='Commands: peek poke keys unlock')
    da_peek = da_cmds.add_parser("peek", help="Read memory")
    da_poke = da_cmds.add_parser("poke", help="Write memory")
    da_keys = da_cmds.add_parser("generatekeys", help="Generate keys")
    da_unlock = da_cmds.add_parser("seccfg", help="Unlock device / Configure seccfg")
    da_rpmb = da_cmds.add_parser("rpmb", help="RPMB Tools")

    da_rpmb_cmds = da_rpmb.add_subparsers(dest='rpmb_subcmd', help='Commands: r w')
    da_rpmb_r = da_rpmb_cmds.add_parser("r", help="Read rpmb")
    da_rpmb_r.add_argument('--filename', type=str, help="Filename to write data into")

    da_rpmb_w = da_rpmb_cmds.add_parser("w", help="Write rpmb")
    da_rpmb_w.add_argument('--filename', type=str, help="Filename to write from")

    da_peek.add_argument('address', type=str, help="Address to read from (hex value)")
    da_peek.add_argument('length', type=str, help="Length to read")
    da_peek.add_argument('--filename', type=str, help="Filename to write data into")

    da_poke.add_argument('address', type=str, help="Address to read from (hex value)")
    da_poke.add_argument('data', type=str, help="Data to write")
    da_poke.add_argument('--filename', type=str, help="Filename to read data from")

    da_unlock.add_argument('flag', type=str, help="Needed flag (unlock,lock)")

    parser_printgpt.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_printgpt.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_printgpt.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_printgpt.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_printgpt.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_printgpt.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_printgpt.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_printgpt.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_printgpt.add_argument('--skipwdt', help='Skip wdt init')
    parser_printgpt.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_printgpt.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_printgpt.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_printgpt.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_printgpt.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_printgpt.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_printgpt.add_argument('--ptype',
                                 help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by ' +
                                      'default)')
    parser_printgpt.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_printgpt.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_printgpt.add_argument('--socid', help='Read Soc ID')

    parser_gpt.add_argument('directory', help='Filename to store gpt files')
    parser_gpt.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_gpt.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_gpt.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_gpt.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_gpt.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_gpt.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_gpt.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_gpt.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_gpt.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_gpt.add_argument('--skipwdt', help='Skip wdt init')
    parser_gpt.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_gpt.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_gpt.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_gpt.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_gpt.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_gpt.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_gpt.add_argument('--ptype',
                            help='Set the payload type ("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_gpt.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_gpt.add_argument('--parttype', help='Partition type\n' +
                                               '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                               '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_gpt.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_gpt.add_argument('--socid', help='Read Soc ID')

    parser_r.add_argument('partitionname', help='Partitions to read (separate by comma for multiple partitions)')
    parser_r.add_argument('filename', help='Filename to store files (separate by comma for multiple filenames)')
    parser_r.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_r.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_r.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_r.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_r.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_r.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_r.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_r.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_r.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_r.add_argument('--skipwdt', help='Skip wdt init')
    parser_r.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_r.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_r.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_r.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_r.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_r.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_r.add_argument('--ptype',
                          help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_r.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_r.add_argument('--parttype', help='Partition type\n' +
                                             '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                             '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_r.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_r.add_argument('--socid', help='Read Soc ID')

    parser_rl.add_argument('directory', help='Directory to write dumped partitions into')
    parser_rl.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_rl.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_rl.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_rl.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_rl.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_rl.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_rl.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_rl.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_rl.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_rl.add_argument('--skipwdt', help='Skip wdt init')
    parser_rl.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_rl.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_rl.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_rl.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_rl.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_rl.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_rl.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_rl.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_rl.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_rl.add_argument('--filename', help='Optional filename')
    parser_rl.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_rl.add_argument('--socid', help='Read Soc ID')

    parser_rf.add_argument('filename', help='Filename to store flash file')
    parser_rf.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_rf.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_rf.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_rf.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_rf.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_rf.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_rf.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_rf.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_rf.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_rf.add_argument('--skipwdt', help='Skip wdt init')
    parser_rf.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_rf.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_rf.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_rf.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_rf.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_rf.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_rf.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_rf.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_rf.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_rf.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')

    parser_rf.add_argument('--filename', help='Optional filename')
    parser_rf.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_rf.add_argument('--socid', help='Read Soc ID')

    parser_rs.add_argument('startsector', help='Sector to start reading (int or hex)')
    parser_rs.add_argument('sectors', help='Sector count')
    parser_rs.add_argument('filename', help='Filename to store sectors')
    parser_rs.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_rs.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_rs.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_rs.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_rs.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_rs.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_rs.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_rs.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_rs.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_rs.add_argument('--skipwdt', help='Skip wdt init')
    parser_rs.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_rs.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_rs.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_rs.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_rs.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_rs.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_rs.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_rs.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_rs.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_rs.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')

    parser_rs.add_argument('--filename', help='Optional filename')
    parser_rs.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_rs.add_argument('--socid', help='Read Soc ID')

    parser_ro.add_argument('offset', help='Offset to start reading (int or hex)')
    parser_ro.add_argument('length', help='Length to read (int or hex)')
    parser_ro.add_argument('filename', help='Filename to store sectors')
    parser_ro.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_ro.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_ro.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_ro.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_ro.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_ro.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_ro.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_ro.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_ro.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_ro.add_argument('--skipwdt', help='Skip wdt init')
    parser_ro.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_ro.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_ro.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_ro.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_ro.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_ro.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_ro.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_ro.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_ro.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_ro.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')

    parser_ro.add_argument('--filename', help='Optional filename')
    parser_ro.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_ro.add_argument('--socid', help='Read Soc ID')

    parser_w.add_argument('partitionname', help='Partition to write (separate by comma for multiple partitions)')
    parser_w.add_argument('filename', help='Filename for writing (separate by comma for multiple filenames)')
    parser_w.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_w.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_w.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_w.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_w.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_w.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_w.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_w.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_w.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_w.add_argument('--skipwdt', help='Skip wdt init')
    parser_w.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_w.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_w.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_w.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_w.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_w.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_w.add_argument('--ptype',
                          help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_w.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_w.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_w.add_argument('--parttype', help='Partition type\n' +
                                             '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                             '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')

    parser_w.add_argument('--filename', help='Optional filename')
    parser_w.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_w.add_argument('--socid', help='Read Soc ID')

    parser_wf.add_argument('filename', help='Filename to write to flash')
    parser_wf.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_wf.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_wf.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_wf.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_wf.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_wf.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_wf.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_wf.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_wf.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_wf.add_argument('--skipwdt', help='Skip wdt init')
    parser_wf.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_wf.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_wf.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_wf.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_wf.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_wf.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_wf.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_wf.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_wf.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_wf.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_wf.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_wf.add_argument('--socid', help='Read Soc ID')

    parser_wl.add_argument('directory', help='Directory with partition filenames to write to flash')
    parser_wl.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_wl.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_wl.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_wl.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_wl.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_wl.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_wl.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_wl.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_wl.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_wl.add_argument('--skipwdt', help='Skip wdt init')
    parser_wl.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_wl.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_wl.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_wl.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_wl.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_wl.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_wl.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_wl.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_wl.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_wl.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_wl.add_argument('--filename', help='Optional filename')
    parser_wl.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_wl.add_argument('--socid', help='Read Soc ID')

    parser_wo.add_argument('offset', help='Offset to start writing (int or hex)')
    parser_wo.add_argument('length', help='Length to write (int or hex)')
    parser_wo.add_argument('filename', help='Filename to write to flash')
    parser_wo.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_wo.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_wo.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_wo.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_wo.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_wo.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_wo.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_wo.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_wo.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_wo.add_argument('--skipwdt', help='Skip wdt init')
    parser_wo.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_wo.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_wo.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_wo.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_wo.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_wo.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_wo.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_wo.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_wo.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_wo.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_wo.add_argument('--filename', help='Optional filename')
    parser_wo.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_wo.add_argument('--socid', help='Read Soc ID')

    parser_e.add_argument('partitionname', help='Partitionname to erase from flash')
    parser_e.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_e.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_e.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_e.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_e.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_e.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_e.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_e.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_e.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_e.add_argument('--skipwdt', help='Skip wdt init')
    parser_e.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_e.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_e.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_e.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_e.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_e.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_e.add_argument('--ptype',
                          help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_e.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_e.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_e.add_argument('--parttype', help='Partition type\n' +
                                             '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                             '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_e.add_argument('--filename', help='Optional filename')
    parser_e.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_e.add_argument('--socid', help='Read Soc ID')

    parser_es.add_argument('partitionname', help='Partitionname to erase from flash')
    parser_es.add_argument('sectors', help='Sectors to erase')
    parser_es.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_es.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_es.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_es.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_es.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_es.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_es.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_es.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_es.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_es.add_argument('--skipwdt', help='Skip wdt init')
    parser_es.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_es.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_es.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_es.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_es.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_es.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_es.add_argument('--ptype',
                           help='Set the payload type ( "amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_es.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_es.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_es.add_argument('--parttype', help='Partition type\n' +
                                              '\t\tEMMC: [user, boot1, boot2, gp1, gp2, gp3, gp4, rpmb]' +
                                              '\t\tUFS: [lu0, lu1, lu2, lu0_lu1]')
    parser_es.add_argument('--filename', help='Optional filename')
    parser_es.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_es.add_argument('--socid', help='Read Soc ID')

    parser_footer.add_argument('filename', help='Filename to store footer')
    parser_footer.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_footer.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_footer.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_footer.add_argument('--sectorsize', default='0x200', help='Set default sector size')
    parser_footer.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_footer.add_argument('--gpt-num-part-entries', default='0', help='Set GPT entry count')
    parser_footer.add_argument('--gpt-part-entry-size', default='0', help='Set GPT entry size')
    parser_footer.add_argument('--gpt-part-entry-start-lba', default='0', help='Set GPT entry start lba sector')
    parser_footer.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_footer.add_argument('--skipwdt', help='Skip wdt init')
    parser_footer.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_footer.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_footer.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_footer.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_footer.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_footer.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_footer.add_argument('--ptype',
                               help='Set the payload type ' +
                                    '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_footer.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_footer.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_footer.add_argument('--filename', help='Optional filename')
    parser_footer.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_footer.add_argument('--socid', help='Read Soc ID')

    parser_dumpbrom.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_dumpbrom.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_dumpbrom.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_dumpbrom.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_dumpbrom.add_argument('--skip', help='Skip reading partition with names "partname1,partname2,etc."')
    parser_dumpbrom.add_argument('--skipwdt', help='Skip wdt init')
    parser_dumpbrom.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_dumpbrom.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_dumpbrom.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_dumpbrom.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_dumpbrom.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_dumpbrom.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_dumpbrom.add_argument('--ptype',
                                 help='Set the payload type ' +
                                      '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_dumpbrom.add_argument('--filename', help='Optional filename')
    parser_dumpbrom.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_dumpbrom.add_argument('--socid', help='Read Soc ID')

    parser_dumppreloader.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_dumppreloader.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_dumppreloader.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_dumppreloader.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_dumppreloader.add_argument('--skipwdt', help='Skip wdt init')
    parser_dumppreloader.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_dumppreloader.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_dumppreloader.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_dumppreloader.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_dumppreloader.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_dumppreloader.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_dumppreloader.add_argument('--ptype',
                                      help='Set the payload type ' +
                                           '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_dumppreloader.add_argument('--preloader', help='Set the preloader filename for dram config')
    parser_dumppreloader.add_argument('--filename', help='Optional filename')
    parser_dumppreloader.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_dumppreloader.add_argument('--socid', help='Read Soc ID')

    parser_payload.add_argument('--payload', type=str, help='Payload filename (optional)')
    parser_payload.add_argument('--loader', type=str, help='Use specific loader, disable autodetection')
    parser_payload.add_argument('--filename', help='Optional payload to load')
    parser_payload.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_payload.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_payload.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_payload.add_argument('--skipwdt', help='Skip wdt init')
    parser_payload.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_payload.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_payload.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_payload.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_payload.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_payload.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_payload.add_argument('--ptype',
                                help='Set the payload type ' +
                                     '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_payload.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_payload.add_argument('--socid', help='Read Soc ID')

    parser_crash.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_crash.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_crash.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_crash.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')

    parser_brute.add_argument('--loader', type=str, help='Use specific loader, disable autodetection')
    parser_brute.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_brute.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_brute.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_brute.add_argument('--skipwdt', help='Skip wdt init')
    parser_brute.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_brute.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_brute.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_brute.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_brute.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_brute.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_brute.add_argument('--ptype',
                              help='Set the payload type ' +
                                   '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_brute.add_argument('--filename', help='Optional filename')
    parser_brute.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_brute.add_argument('--socid', help='Read Soc ID')

    parser_gettargetconfig.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_gettargetconfig.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_gettargetconfig.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_gettargetconfig.add_argument('--socid', help='Read Soc ID')

    parser_peek.add_argument('address', help='Address to read from memory')
    parser_peek.add_argument('length', help='Bytes to read from memory')
    parser_peek.add_argument('--filename', help='Optional filename to write dumped data')
    parser_peek.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_peek.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_peek.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_peek.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_peek.add_argument('--skipwdt', help='Skip wdt init')
    parser_peek.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_peek.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_peek.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_peek.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_peek.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_peek.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_peek.add_argument('--ptype',
                             help='Set the payload type ' +
                                  '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_peek.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_peek.add_argument('--socid', help='Read Soc ID')

    parser_stage.add_argument('--payload', type=str, help='Payload filename (optional)')
    parser_stage.add_argument('--stage2', help='Set stage2 filename')
    parser_stage.add_argument('--stage2addr', help='Set stage2 loading address')
    parser_stage.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_stage.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_stage.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_stage.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_stage.add_argument('--skipwdt', help='Skip wdt init')
    parser_stage.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_stage.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_stage.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_stage.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_stage.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_stage.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_stage.add_argument('--ptype',
                              help='Set the payload type ' +
                                   '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_stage.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_stage.add_argument('--filename', help='Optional filename')
    parser_stage.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_stage.add_argument('--socid', help='Read Soc ID')

    parser_plstage.add_argument('--payload', type=str, help='Payload filename (optional)')
    parser_plstage.add_argument('--pl', help='pl stage filename (optional)')
    parser_plstage.add_argument('--loader', type=str, help='Use specific DA loader, disable autodetection')
    parser_plstage.add_argument('--vid', type=str, help='Set usb vendor id used for MTK Preloader')
    parser_plstage.add_argument('--pid', type=str, help='Set usb product id used for MTK Preloader')
    parser_plstage.add_argument('--debugmode', action='store_true', default=False, help='Enable verbose mode')
    parser_plstage.add_argument('--skipwdt', help='Skip wdt init')
    parser_plstage.add_argument('--wdt', help='Set a specific watchdog addr')
    parser_plstage.add_argument('--mode', help='Set a crash mode (0=dasend1,1=dasend2,2=daread)')
    parser_plstage.add_argument('--var1', help='Set kamakiri specific var1 value')
    parser_plstage.add_argument('--uart_addr', help='Set payload uart_addr value')
    parser_plstage.add_argument('--da_addr', help='Set a specific da payload addr')
    parser_plstage.add_argument('--brom_addr', help='Set a specific brom payload addr')
    parser_plstage.add_argument('--ptype',
                                help='Set the payload type ' +
                                     '("amonet","kamakiri","kamakiri2", kamakiri2/da used by default)')
    parser_plstage.add_argument('--preloader', help='Set the preloader filename for loading')
    parser_plstage.add_argument('--verifystage2', help='Verify if stage2 data has been written correctly')
    parser_plstage.add_argument('--crash', help='Enforce crash if device is in pl mode to enter brom mode')
    parser_plstage.add_argument('--socid', help='Read Soc ID')
    parser_plstage.add_argument('--startpartition', help='Option for plstage - Boot to (lk, tee1)')

    parser_printgpt.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_footer.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_e.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_es.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_wl.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_wf.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_w.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_rs.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_rf.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_rl.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_gpt.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')
    parser_r.add_argument('--generatekeys', action="store_true", help='Option for deriving hw keys')

    args = parser.parse_args()
    cmd = args.cmd
    if cmd not in cmds:
        showcommands()
        exit(0)

    mtk = Main(args).run()
