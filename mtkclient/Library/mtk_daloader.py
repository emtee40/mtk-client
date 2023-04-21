#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import json
import logging
import os
import hashlib
from binascii import hexlify
from mtkclient.Library.utils import LogBase, logsetup, progress
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.daconfig import DAconfig
from mtkclient.Library.mtk_dalegacy import DALegacy, norinfo, emmcinfo, sdcinfo, nandinfo64
from mtkclient.Library.mtk_daxflash import DAXFlash
from mtkclient.config.brom_config import damodes
from mtkclient.Library.xflash_ext import xflashext
from mtkclient.Library.legacy_ext import legacyext
from mtkclient.Library.settings import hwparam


class DAloader(metaclass=LogBase):
    def __init__(self, mtk, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.mtk = mtk
        self.config = mtk.config
        self.loglevel = loglevel
        self.eh = ErrorHandler()
        self.config = self.mtk.config
        self.usbwrite = self.mtk.port.usbwrite
        self.usbread = self.mtk.port.usbread
        self.echo = self.mtk.port.echo
        self.rbyte = self.mtk.port.rbyte
        self.rdword = self.mtk.port.rdword
        self.rword = self.mtk.port.rword
        self.daconfig = DAconfig(mtk=self.mtk, loader=self.mtk.config.loader,
                                 preloader=self.mtk.config.preloader, loglevel=loglevel)
        self.hwparam = hwparam(mtk.config.meid)
        self.progress = progress(self.daconfig.pagesize, self.mtk.config.guiprogress)
        self.xft = None
        self.lft = None
        self.da = None
        self.xflash = None

    def writestate(self):
        config = {}
        config["xflash"] = self.mtk.config.chipconfig.damode == damodes.XFLASH
        config["hwcode"] = self.config.hwcode
        if self.config.meid is not None:
            config["meid"] = hexlify(self.config.meid).decode('utf-8')
        if self.config.socid is not None:
            config["socid"] = hexlify(self.config.socid).decode('utf-8')
        config["flashtype"] = self.daconfig.flashtype
        config["flashsize"] = self.daconfig.flashsize
        if not self.mtk.config.chipconfig.damode == damodes.XFLASH:
            config["m_emmc_ua_size"] = self.da.emmc.m_emmc_ua_size
            config["m_emmc_boot1_size"] = self.da.emmc.m_emmc_boot1_size
            config["m_emmc_boot2_size"] = self.da.emmc.m_emmc_boot2_size
            config["m_emmc_gp_size"] = self.da.emmc.m_emmc_gp_size
            config["m_nand_flash_size"] = self.da.nand.m_nand_flash_size
            config["m_nor_flash_size"] = self.da.nor.m_nor_flash_size
            if not self.mtk.config.iot:
                config["m_sdmmc_ua_size"] = self.da.sdc.m_sdmmc_ua_size

        open(".state", "w").write(json.dumps(config))

    def compute_hash_pos(self, da1, da2, da2sig_len):
        hashlen = len(da2) - da2sig_len

        hashmode, idx = self.calc_da_hash(da1, da2[:hashlen])
        if idx == -1:
            hashlen = len(da2)
            hashmode, idx = self.calc_da_hash(da1, da2[:hashlen])
            if idx == -1:
                self.error("Hash computation failed.")
                return None, None, None
            return idx, hashmode, hashlen
        return idx, hashmode, hashlen

    def calc_da_hash(self, da1, da2):
        hashdigest = hashlib.sha1(da2).digest()
        hashdigest256 = hashlib.sha256(da2).digest()
        idx = da1.find(hashdigest)
        hashmode = 1
        if idx == -1:
            idx = da1.find(hashdigest256)
            hashmode = 2
        return hashmode, idx

    def fix_hash(self, da1, da2, hashpos, hashmode, hashlen):
        da1 = bytearray(da1)
        dahash = None
        if hashmode == 1:
            dahash = hashlib.sha1(da2[:hashlen]).digest()
        elif hashmode == 2:
            dahash = hashlib.sha256(da2[:hashlen]).digest()
        orighash=da1[hashpos:hashpos + len(dahash)]
        da1[hashpos:hashpos + len(dahash)] = dahash
        return da1

    def reinit(self):
        if os.path.exists(".state"):
            config = json.loads(open(".state", "r").read())
            self.config.hwcode = config["hwcode"]
            if "meid" in config:
                self.config.meid = bytes.fromhex(config["meid"])
            if "socid" in config:
                self.config.socid = bytes.fromhex(config["socid"])
            self.xflash = config["xflash"]
            self.config.init_hwcode(self.config.hwcode)
            if self.xflash:
                self.da = DAXFlash(self.mtk, self.daconfig, self.loglevel)
                self.daconfig.flashtype = config["flashtype"]
                self.daconfig.flashsize = config["flashsize"]
                self.da.reinit()
                self.xft = xflashext(self.mtk, self.da, self.loglevel)
                self.lft = None
            else:
                self.da = DALegacy(self.mtk, self.daconfig, self.loglevel)
                self.daconfig.flashtype = config["flashtype"]
                self.daconfig.flashsize = config["flashsize"]
                self.da.nor = norinfo()
                self.da.nand = nandinfo64()
                self.da.emmc = emmcinfo(self.config)
                self.da.sdc = sdcinfo(self.config)
                self.lft = legacyext(self.mtk, self.da, self.loglevel)
                self.da.emmc.m_emmc_ua_size = config["m_emmc_ua_size"]
                self.da.emmc.m_emmc_boot1_size = config["m_emmc_boot1_size"]
                self.da.emmc.m_emmc_boot2_size = config["m_emmc_boot2_size"]
                self.da.emmc.m_emmc_gp_size = config["m_emmc_gp_size"]
                self.da.nand.m_nand_flash_size = config["m_nand_flash_size"]
                self.da.sdc.m_sdmmc_ua_size = config["m_sdmmc_ua_size"]
                self.da.nor.m_nor_flash_size = config["m_nor_flash_size"]
                self.xft = None
            return True
        return False

    def set_da(self):
        self.xflash = False
        if self.mtk.config.plcap is not None:
            PL_CAP0_XFLASH_SUPPORT = (0x1 << 0)
            if self.mtk.config.plcap[
                0] & PL_CAP0_XFLASH_SUPPORT == PL_CAP0_XFLASH_SUPPORT and self.mtk.config.blver > 1:
                self.xflash = True
        if self.mtk.config.chipconfig.damode == 1:
            self.xflash = True
        if self.xflash:
            self.da = DAXFlash(self.mtk, self.daconfig, self.loglevel)
            self.xft = xflashext(self.mtk, self.da, self.loglevel)
        else:
            self.da = DALegacy(self.mtk, self.daconfig, self.loglevel)
            self.lft = legacyext(self.mtk, self.da, self.loglevel)

    def setmetamode(self, porttype: str):
        self.xflash = False
        if self.mtk.config.chipconfig.damode == 1:
            self.xflash = True
        if self.xflash:
            self.da = DAXFlash(self.mtk, self.daconfig, self.loglevel)
            if porttype not in ["off", "usb", "uart"]:
                self.error("Only \"off\",\"usb\" or \"uart\" are allowed.")
            if self.da.set_meta(porttype):
                self.info(f"Successfully set meta mode to {porttype}")
                return True
            else:
                self.error("Setting meta mode in xflash failed.")
        self.error("Device is not in xflash mode, cannot run meta cmd.")
        return False

    def detect_partition(self, partitionname, parttype=None):
        fpartitions = []
        data, guid_gpt = self.da.partition.get_gpt(self.mtk.config.gpt_settings, parttype)
        if guid_gpt is None:
            return [False, fpartitions]
        else:
            for partition in guid_gpt.partentries:
                fpartitions.append(partition)
                if partition.name.lower() == partitionname.lower():
                    return [True, partition]
        return [False, fpartitions]

    def get_partition_data(self, parttype=None):
        fpartitions = []
        data, guid_gpt = self.da.partition.get_gpt(self.mtk.config.gpt_settings, parttype)
        if guid_gpt is None:
            return [False, fpartitions]
        else:
            return guid_gpt.partentries

    def get_gpt(self, parttype=None):
        fpartitions = []
        data, guid_gpt = self.da.partition.get_gpt(self.mtk.config.gpt_settings, parttype)
        if guid_gpt is None:
            return [False, fpartitions]
        return [data, guid_gpt]

    def upload(self):
        return self.da.upload()

    class ShutDownModes:
        NORMAL = 0
        HOME_SCREEN = 1
        FASTBOOT = 2

    def shutdown(self, bootmode=ShutDownModes.NORMAL):
        return self.da.shutdown(async_mode=0, dl_bit=0, bootmode=bootmode)

    def upload_da(self, preloader=None):
        self.daconfig.setup()
        self.daconfig.extract_emi(preloader)
        self.set_da()
        return self.da.upload_da()

    def writeflash(self, addr, length, filename, offset=0, parttype=None, wdata=None, display=True):
        return self.da.writeflash(addr=addr, length=length, filename=filename, offset=offset,
                                  parttype=parttype, wdata=wdata, display=display)

    def formatflash(self, addr, length, partitionname, parttype, display=True):
        return self.da.formatflash(addr=addr, length=length, parttype=parttype)

    def readflash(self, addr, length, filename, parttype, display=True):
        return self.da.readflash(addr=addr, length=length, filename=filename, parttype=parttype, display=display)

    def get_packet_length(self):
        if self.xflash:
            pt = self.da.get_packet_length()
            return pt.read_packet_length
        else:
            return 512

    def peek(self, addr: int, length: int):
        if self.xflash:
            return self.xft.custom_read(addr=addr, length=length)
        else:
            return self.lft.custom_read(addr=addr, length=length)

    def poke(self, addr: int, data: bytes or bytearray):
        if self.xflash:
            return self.xft.custom_write(addr=addr, data=data)
        else:
            return self.lft.custom_write(addr=addr, data=data)

    def keys(self):
        if self.xflash:
            return self.xft.generate_keys()
        else:
            return self.lft.generate_keys()

    def is_patched(self):
        return self.da.patch

    def seccfg(self, lockflag):
        if self.xflash:
            return self.xft.seccfg(lockflag)
        else:
            return self.lft.seccfg(lockflag)

    def read_rpmb(self, filename=None):
        if self.xflash:
            return self.xft.read_rpmb(filename)
        self.error("Device is not in xflash mode, cannot run read rpmb cmd.")
        return False

    def write_rpmb(self, filename=None):
        if self.xflash:
            return self.xft.write_rpmb(filename)
        self.error("Device is not in xflash mode, cannot run write rpmb cmd.")
        return False

    def erase_rpmb(self):
        if self.xflash:
            return self.xft.erase_rpmb()
        self.error("Device is not in xflash mode, cannot run erase rpmb cmd.")
        return False
