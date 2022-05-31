#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import os
import logging
from binascii import hexlify
from struct import pack, unpack
from mtkclient.config.payloads import pathconfig
from mtkclient.Library.utils import LogBase, print_progress, logsetup
from mtkclient.Library.hwcrypto import crypto_setup, hwcrypto
from mtkclient.Library.kamakiri import Kamakiri
from mtkclient.Library.Port import Port


class PLTools(metaclass=LogBase):
    def __init__(self, mtk, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.mtk = mtk
        self.chipconfig = self.mtk.config.chipconfig
        self.config = self.mtk.config
        self.usbwrite = self.mtk.port.usbwrite
        self.usbread = self.mtk.port.usbread
        self.read32 = self.mtk.preloader.read32
        self.write32 = self.mtk.preloader.write32
        self.hwcode = mtk.config.hwcode

        # exploit types
        self.kama = Kamakiri(self.mtk, self.__logger.level)

        # crypto types
        setup = crypto_setup()
        setup.hwcode = self.mtk.config.hwcode
        setup.dxcc_base = self.mtk.config.chipconfig.dxcc_base
        setup.read32 = self.mtk.preloader.read32
        setup.write32 = self.mtk.preloader.write32
        setup.writemem = self.mtk.preloader.writemem
        setup.da_payload_addr = self.mtk.config.chipconfig.da_payload_addr
        setup.gcpu_base = self.mtk.config.chipconfig.gcpu_base
        setup.blacklist = self.mtk.config.chipconfig.blacklist
        setup.sej_base = self.mtk.config.chipconfig.sej_base
        setup.cqdma_base = self.mtk.config.chipconfig.cqdma_base
        setup.ap_dma_mem = self.mtk.config.chipconfig.ap_dma_mem
        setup.meid_addr = self.mtk.config.chipconfig.meid_addr
        setup.prov_addr = self.mtk.config.chipconfig.prov_addr
        self.hwcrypto = hwcrypto(setup, loglevel, self.mtk.config.gui)

        self.pathconfig = pathconfig()
        if loglevel == logging.DEBUG:
            logfilename = os.path.join("logs", "log.txt")
            fh = logging.FileHandler(logfilename, encoding='utf-8')
            self.__logger.addHandler(fh)
            self.__logger.setLevel(logging.DEBUG)
        else:
            self.__logger.setLevel(logging.INFO)

    def runpayload(self, filename, offset=0, ack=0xA1A2A3A4, addr=None, dontack=False):
        ptype = self.config.ptype
        try:
            with open(filename, "rb") as rf:
                rf.seek(offset)
                payload = rf.read()
                self.info(f"Loading payload from {os.path.basename(filename)}, {hex(len(payload))} bytes")
        except FileNotFoundError:
            self.info(f"Couldn't open {filename} for reading.")
            return False

        if addr is None:
            if ptype == "amonet":
                addr = self.chipconfig.da_payload_addr
            elif ptype == "kamakiri":
                addr = self.chipconfig.brom_payload_addr
                exploittype = 1
            elif ptype == "kamakiri2":
                addr = self.chipconfig.brom_payload_addr
                exploittype = 2
            elif ptype == "hashimoto":
                addr = self.chipconfig.da_payload_addr
            elif ptype == "carbonara":
                addr = self.chipconfig.brom_payload_addr
            elif ptype == "":
                if self.mtk.config.target_config["sla"] or self.mtk.config.target_config["daa"]:
                    addr = self.chipconfig.brom_payload_addr
                else:
                    addr = self.chipconfig.da_payload_addr

        if ptype == "amonet":
            self.info("Amonet Run")
            if self.payload(payload, addr, ptype):
                if dontack:
                    return True
                result = self.usbread(4)
                if result == pack(">I", ack):
                    self.info("Successfully sent payload: " + filename)
                    return True
                self.info("Error, payload answered instead: " + hexlify(result).decode('utf-8'))
                return False
            else:
                self.error("Error on sending payload: " + filename)
            return True
        elif ptype in ("kamakiri", "kamakiri2"):
            self.info("Kamakiri / DA Run")
            if self.kama.payload(payload, addr, True, exploittype):
                if dontack:
                    return True
                result = self.usbread(4)
                if result == pack(">I", ack):
                    self.info("Successfully sent payload: " + filename)
                    return True
                self.info("Error, payload answered instead: " + hexlify(result).decode('utf-8'))
                return False
            else:
                self.error("Error on sending payload: " + filename)
        elif ptype == "hashimoto":
            self.info("Hashimoto Run")
            if self.payload(payload, addr, "cqdma"):
                if dontack:
                    return True
                result = self.usbread(4)
                if result == pack(">I", ack):
                    self.info("Successfully sent payload: " + filename)
                    return True
                self.info("Error, payload answered instead: " + hexlify(result).decode('utf-8'))
                return False
            else:
                self.error("Error on sending payload: " + filename)
        elif ptype == "carbonara":
            self.info("Carbonara is best served at local restaurants.")
        else:
            self.info("Kamakiri / DA Run")
            if self.kama.payload(payload, addr, False, exploittype=2):
                if dontack:
                    return True
                result = self.usbread(4)
                if result == pack(">I", ack):
                    self.info("Successfully sent payload: " + filename)
                    return True
                if result == b"\xc1\xc2\xc3\xc4":
                    if "preloader" in rf.name:
                        ack = self.mtk.port.usbread(4)
                        if ack == b"\xC0\xC0\xC0\xC0":
                            with open("preloader.bin", 'wb') as wf:
                                print_progress(0, 100, prefix='Progress:', suffix='Complete', bar_length=50)
                                for pos in range(0, 0x40000, 64):
                                    wf.write(self.mtk.port.usbread(64))
                                self.info("Preloader dumped as: " + "preloader.bin")
                                return True
                    else:
                        with open("out.bin", 'wb') as wf:
                            print_progress(0, 100, prefix='Progress:', suffix='Complete', bar_length=50)
                            for pos in range(0, 0x20000, 64):
                                wf.write(self.mtk.port.usbread(64))
                            self.info("Bootrom dumped as: " + "out.bin")
                            return True
                self.info("Error, payload answered instead: " + hexlify(result).decode('utf-8'))
                return False
            else:
                self.error("Error on sending payload: " + filename)

    def runbrute(self, args):
        if self.config.ptype == "kamakiri":
            self.info("Kamakiri Run")
            if self.kama.bruteforce(args):
                return True
            else:
                self.error("Error on bruteforcing.")
        elif self.config.ptype == "kamakiri2":
            self.info("Kamakiri2 Run")
            if self.kama.bruteforce2(args, 0x9900):
                return True
            else:
                self.error("Error on bruteforcing.")
        return False

    def crash(self, mode=0):
        self.info("Crashing da...")
        try:
            if mode == 1:
                self.mtk.preloader.send_da(0, 0x100, 0x100, b'\x00' * 0x100)
            elif mode == 2:
                self.mtk.preloader.read32(0, 0x100)
            elif mode == 0:
                payload = b'\x00\x01\x9F\xE5\x10\xFF\x2F\xE1' + b'\x00' * 0x110
                self.mtk.preloader.send_da(0x0, len(payload), 0x0, payload)
                self.mtk.preloader.jump_da(0x0)
        except:
            pass

    def crasher(self, mtk, enforcecrash: bool = False):
        plt = PLTools(mtk, self.__logger.level)
        if enforcecrash or self.config.meid is None:
            self.info("We're not in bootrom, trying to crash da...")
            for crashmode in range(0, 3):
                try:
                    plt.crash(crashmode)
                except Exception as e:
                    self.__logger.debug(str(e))
                    pass
                portconfig = [[0xE8D, 0x0003, 1]]
                mtk.port = Port(mtk=mtk, portconfig=portconfig, serialportname=mtk.port.serialportname,
                                loglevel=self.__logger.level)
                if mtk.preloader.init(maxtries=20):
                    break
        return mtk

    def run_dump_brom(self, filename, btype, loader="generic_dump_payload.bin"):
        length = 0x20000
        if loader == "generic_sram_payload.bin":
            length = 0x200000
        pfilename = os.path.join(self.pathconfig.get_payloads_path(), loader)
        if btype == "amonet":
            if self.dump_brom(filename, "gcpu", length=length):
                self.info("Dumped as: " + filename)
                return True
            else:
                self.error("Error on sending payload: " + pfilename)
        elif btype == "hashimoto":
            if self.dump_brom(filename, "cqdma", length=length):
                self.info("Dumped as: " + filename)
                return True
            else:
                self.error("Error on sending payload: " + pfilename)
        elif btype == "kamakiri":
            self.info("Kamakiri / DA Run")
            if self.runpayload(filename=pfilename, ack=0xC1C2C3C4, offset=0):
                if self.kama.dump_brom(filename):
                    self.info("Dumped as: " + filename)
                    return True
            else:
                self.error("Error on sending payload: " + filename)
        elif btype == "kamakiri2" or btype is None:
            self.info("Kamakiri2")
            if self.mtk.config.chipconfig.send_ptr[0] is None:
                self.info("Unknown chipset, please run \"brute\" command and send the brom as an issue on github")
                return False
            if self.runpayload(filename=pfilename, ack=0xC1C2C3C4, offset=0):
                if self.kama.dump_brom(filename):
                    self.info("Dumped as: " + filename)
                    return True
            else:
                self.error("Error on sending payload: " + filename)
        elif btype == "carbonara":
            self.info("Carbonara is best served at local restaurants.")
            return False
        else:
            self.error("Unknown dumpbrom ptype: " + btype)
            self.info("Available ptypes are: amonet, kamakiri, kamakiri2, hashimoto, carbonara")
        self.error("Error on dumping.")
        return False

    def run_dump_preloader(self, btype):
        pfilename = os.path.join(self.pathconfig.get_payloads_path(), "generic_preloader_dump_payload.bin")
        """
        if btype == "amonet":
            if self.dump_brom(filename, "gcpu"):
                self.info("Preloader dumped as: " + filename)
                return True
            else:
                self.error("Error on sending payload: " + pfilename)
        elif btype == "hashimoto":
            if self.dump_brom(filename, "cqdma"):
                self.info("Preloader dumped as: " + filename)
                return True
            else:
                self.error("Error on sending payload: " + pfilename)
        """
        if btype == "kamakiri":
            self.info("Kamakiri / DA Run")
            if self.runpayload(filename=pfilename, ack=0xC1C2C3C4, offset=0):
                data, filename = self.kama.dump_preloader()
                return data, filename
            else:
                self.error("Error on sending payload: " + pfilename)
                return None, None
        elif btype == "kamakiri2" or btype is None:
            self.info("Kamakiri2")
            if self.runpayload(filename=pfilename, ack=0xC1C2C3C4, offset=0):
                data, filename = self.kama.dump_preloader()
                return data, filename
            else:
                self.error("Error on sending payload: " + pfilename)
                return None, None
        elif btype == "carbonara":
            self.info("Carbonara is best served at local restaurants.")
            return None, None
        else:
            self.error("Unknown dumpbrom ptype: " + btype)
            self.info("Available ptypes are: amonet, kamakiri, kamakiri2, hashimoto, carbonara")
        self.error("Error on dumping Bootrom.")
        return False

    def run_crypto(self, data, iv, btype="sej", encrypt=True):
        if data is None:
            data = bytearray()
        for i in range(32):
            data.append(self.config.meid[i % len(self.config.meid)])
        if btype == "":
            encrypted = self.hwcrypto.aes_hwcrypt(data=data, iv=iv, encrypt=encrypt, btype=btype)
            return encrypted
        return False

    def dump_brom(self, filename, btype, length=0x20000):
        if btype == "gcpu" and self.chipconfig.gcpu_base is None:
            self.error("Chipconfig has no gcpu_base field for this cpu")
            return False
        elif btype == "cqdma" and self.chipconfig.cqdma_base is None or self.chipconfig.ap_dma_mem is None:
            self.error("Chipconfig has no cqdma_base and/or ap_dma_mem field for this cpu")
            return False
        if self.chipconfig.blacklist:
            self.hwcrypto.disable_range_blacklist(btype, self.mtk)
        self.info("Dump bootrom")
        print_progress(0, 100, prefix='Progress:', suffix='Complete', bar_length=50)
        old = 0
        with open(filename, 'wb') as wf:
            for addr in range(0x0, length, 16):
                prog = int(addr / length * 100)
                if round(prog, 1) > old:
                    print_progress(prog, 100, prefix='Progress:', suffix='Complete, addr %08X' % addr,
                                   bar_length=50)
                    old = round(prog, 1)
                if btype == "gcpu":
                    wf.write(self.hwcrypto.gcpu.aes_read_cbc(addr))
                elif btype == "cqdma":
                    if not self.chipconfig.blacklist:
                        wf.write(self.hwcrypto.cqdma.mem_read(addr, 16, True))
                    else:
                        wf.write(self.hwcrypto.cqdma.mem_read(addr, 16, False))
        print_progress(100, 100, prefix='Progress:', suffix='Complete', bar_length=50)
        return True

    def dump_preloader(self, filename, btype):
        if btype == "gcpu" and self.chipconfig.gcpu_base is None:
            self.error("Chipconfig has no gcpu_base field for this cpu")
            return False
        elif btype == "cqdma" and self.chipconfig.cqdma_base is None or self.chipconfig.ap_dma_mem is None:
            self.error("Chipconfig has no cqdma_base and/or ap_dma_mem field for this cpu")
            return False
        if self.chipconfig.blacklist:
            self.hwcrypto.disable_range_blacklist(btype, self.mtk)
        self.info("Dump bootrom")
        print_progress(0, 100, prefix='Progress:', suffix='Complete', bar_length=50)
        old = 0
        with open(filename, 'wb') as wf:
            for addr in range(0x200000, 0x240000, 16):
                prog = int(addr / 0x20000 * 100)
                if round(prog, 1) > old:
                    print_progress(prog, 100, prefix='Progress:', suffix='Complete, addr %08X' % addr,
                                   bar_length=50)
                    old = round(prog, 1)
                if btype == "gcpu":
                    wf.write(self.hwcrypto.gcpu.aes_read_cbc(addr))
                elif btype == "cqdma":
                    if not self.chipconfig.blacklist:
                        wf.write(self.hwcrypto.cqdma.mem_read(addr, 16, True))
                    else:
                        wf.write(self.hwcrypto.cqdma.mem_read(addr, 16, False))
        print_progress(100, 100, prefix='Progress:', suffix='Complete', bar_length=50)
        return True

    def payload(self, payload, daaddr, ptype):
        self.hwcrypto.disable_range_blacklist(ptype, self.mtk.preloader.run_ext_cmd)
        try:
            while len(payload) % 4 != 0:
                payload += b"\x00"

            words = []
            for x in range(len(payload) // 4):
                word = payload[x * 4:(x + 1) * 4]
                word = unpack("<I", word)[0]
                words.append(word)

            self.info("Sending payload")
            self.write32(self, words)

            self.info("Running payload ...")
            self.write32(self.mtk.config.chipconfig.blacklist[0][0] + 0x40, daaddr)
            return True
        except Exception as e:
            self.error("Failed to load payload file. Error: " + str(e))
            return False
