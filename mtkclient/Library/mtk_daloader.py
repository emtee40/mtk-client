#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 MIT License
import logging
from mtkclient.Library.utils import LogBase, logsetup
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.daconfig import DAconfig
from mtkclient.Library.mtk_dalegacy import DALegacy
from mtkclient.Library.mtk_daxflash import DAXFlash


class DAloader(metaclass=LogBase):
    def __init__(self, mtk, loader=None, preloader=None, generatekeys=None, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel)
        self.mtk = mtk
        self.generatekeys = generatekeys
        self.loader = loader
        self.loglevel = loglevel
        self.eh = ErrorHandler()
        self.config = self.mtk.config
        self.usbwrite = self.mtk.port.usbwrite
        self.usbread = self.mtk.port.usbread
        self.echo = self.mtk.port.echo
        self.rbyte = self.mtk.port.rbyte
        self.rdword = self.mtk.port.rdword
        self.rword = self.mtk.port.rword
        self.daconfig = DAconfig(mtk=self.mtk, loader=loader, preloader=preloader, loglevel=loglevel)
        self.da = None

    def set_da(self):
        xflash = False
        if self.mtk.config.plcap is not None:
            PL_CAP0_XFLASH_SUPPORT = (0x1 << 0)
            if self.mtk.config.plcap[
                0] & PL_CAP0_XFLASH_SUPPORT == PL_CAP0_XFLASH_SUPPORT and self.mtk.config.blver > 1:
                xflash = True
        if self.mtk.config.chipconfig.damode == 1:
            xflash = True
        if xflash:
            self.da = DAXFlash(self.mtk, self.daconfig, self.generatekeys, self.loglevel)
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
        self.daconfig.extract_emi(preloader,legacy=self.mtk.config.chipconfig.damode==0)
        self.set_da()
        return self.da.upload_da()

    def writeflash(self, addr, length, filename, partitionname, offset=0, parttype=None, display=True):
        return self.da.writeflash(addr=addr, length=length, filename=filename, offset=offset,
                                  partitionname=partitionname, parttype=parttype, display=display)

    def formatflash(self, addr, length, partitionname, parttype, display=True):
        return self.da.formatflash(addr=addr, length=length, parttype=parttype)

    def readflash(self, addr, length, filename, parttype, display=True):
        return self.da.readflash(addr=addr, length=length, filename=filename, parttype=parttype, display=display)
