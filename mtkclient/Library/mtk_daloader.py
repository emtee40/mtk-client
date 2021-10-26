#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 MIT License
import json
import logging
import os
from mtkclient.Library.utils import LogBase, logsetup
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.daconfig import DAconfig
from mtkclient.Library.mtk_dalegacy import DALegacy, norinfo, emmcinfo, sdcinfo, nandinfo64
from mtkclient.Library.mtk_daxflash import DAXFlash
from mtkclient.config.brom_config import damodes
from mtkclient.Library.xflash_ext import xflashext

class DAloader(metaclass=LogBase):
    def __init__(self, mtk, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel)
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
        self.xft = None
        self.da = None

    def writestate(self):
        config = {}
        config["xflash"] = self.mtk.config.chipconfig.damode==damodes.XFLASH
        config["hwcode"] = self.config.hwcode
        config["flashtype"] = self.daconfig.flashtype
        config["flashsize"] = self.daconfig.flashsize
        if not self.mtk.config.chipconfig.damode==damodes.XFLASH:
            config["m_emmc_ua_size"] = self.da.emmc.m_emmc_ua_size
            config["m_emmc_boot1_size"] = self.da.emmc.m_emmc_boot1_size
            config["m_emmc_boot2_size"] = self.da.emmc.m_emmc_boot2_size
            config["m_emmc_gp_size"] = self.da.emmc.m_emmc_gp_size
            config["m_nand_flash_size"] = self.da.nand.m_nand_flash_size
            config["m_sdmmc_ua_size"] = self.da.sdc.m_sdmmc_ua_size
            config["m_nor_flash_size"] = self.da.nor.m_nor_flash_size

        open(".state", "w").write(json.dumps(config))

    def reinit(self):
        if os.path.exists(".state"):
            config = json.loads(open(".state", "r").read())
            self.config.hwcode = config["hwcode"]
            self.xflash = config["xflash"]
            self.config.init_hwcode(self.config.hwcode)
            if self.xflash:
                self.da = DAXFlash(self.mtk, self.daconfig, self.loglevel)
                self.daconfig.flashtype = config["flashtype"]
                self.daconfig.flashsize = config["flashsize"]
                self.da.reinit()
                self.xft=xflashext(self.mtk, self.da, self.loglevel)
            else:
                self.da = DALegacy(self.mtk, self.daconfig, self.loglevel)
                self.daconfig.flashtype = config["flashtype"]
                self.daconfig.flashsize = config["flashsize"]
                self.da.nor = norinfo()
                self.da.nand = nandinfo64()
                self.da.emmc = emmcinfo()
                self.da.sdc = sdcinfo()

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

    def detect_partition(self, arguments, partitionname, parttype=None):
        fpartitions = []
        data, guid_gpt = self.da.partition.get_gpt(int(arguments.gpt_num_part_entries),
                                                   int(arguments.gpt_part_entry_size),
                                                   int(arguments.gpt_part_entry_start_lba), parttype)
        if guid_gpt is None:
            return [False, fpartitions]
        else:
            for partition in guid_gpt.partentries:
                fpartitions.append(partition)
                if partition.name.lower() == partitionname.lower():
                    return [True, partition]
        return [False, fpartitions]

    def get_partition_data(self, arguments, parttype=None):
        fpartitions = []
        data, guid_gpt = self.da.partition.get_gpt(int(arguments.gpt_num_part_entries),
                                                   int(arguments.gpt_part_entry_size),
                                                   int(arguments.gpt_part_entry_start_lba), parttype)
        if guid_gpt is None:
            return [False, fpartitions]
        else:
            return guid_gpt.partentries

    def get_gpt(self, arguments, parttype=None):
        fpartitions = []
        data, guid_gpt = self.da.partition.get_gpt(int(arguments.gpt_num_part_entries),
                                                   int(arguments.gpt_part_entry_size),
                                                   int(arguments.gpt_part_entry_start_lba), parttype)
        if guid_gpt is None:
            return [False, fpartitions]
        return [data, guid_gpt]

    def upload(self):
        return self.da.upload()

    def close(self):
        return self.da.close()

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

    def peek(self, addr: int, length:int):
        if self.xflash:
            return self.xft.custom_read(addr=addr, length=length)
        self.error("Device is not in xflash mode, cannot run peek cmd.")
        return b""

    def poke(self, addr: int, data: bytes or bytearray):
        if self.xflash:
            return self.xft.custom_write(addr=addr, data=data)
        self.error("Device is not in xflash mode, cannot run poke cmd.")
        return False

    def keys(self):
        if self.xflash:
            return self.xft.generate_keys()
        self.error("Device is not in xflash mode, cannot run keys cmd.")
        return False

    def seccfg(self, lockflag):
        if self.xflash:
            return self.xft.seccfg(lockflag)
        self.error("Device is not in xflash mode, cannot run unlock cmd.")
        return False

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