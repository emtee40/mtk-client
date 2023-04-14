#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import logging

from mtkclient.Library.utils import LogBase, logsetup
from mtkclient.Library.gpt import gpt


class Partition(metaclass=LogBase):
    def __init__(self, mtk, readflash, read_pmt, loglevel=logging.INFO):
        self.mtk = mtk
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.config = self.mtk.config
        self.readflash = readflash
        self.read_pmt = read_pmt
        if self.config.gpt_file is not None:
            self.gptfilename = self.config.gpt_file
            self.readflash = self.readflash_override

    def readflash_override(self, addr:int, length:int,filename:str="",parttype:str="",display:bool=False):
        with open(self.gptfilename,"rb") as rf:
            rf.seek(addr)
            data=rf.read(length)
            if filename == "":
                return data
        return None

    def get_gpt(self, gpt_settings, parttype="user"):
        data = self.readflash(addr=0, length=2 * self.config.pagesize, filename="", parttype=parttype, display=False)
        if data[:4] == b"BPI\x00":
            guid_gpt = gpt(
                num_part_entries=gpt_settings.gpt_num_part_entries,
                part_entry_size=gpt_settings.gpt_part_entry_size,
                part_entry_start_lba=gpt_settings.gpt_part_entry_start_lba,
            )
            data = self.readflash(addr=0, length=32 * self.config.pagesize, filename="",
                                  parttype=parttype, display=False)
            if data == b"":
                return None, None
            guid_gpt.parse_bpi(data, self.config.pagesize)
            return data, guid_gpt
        if data[:9] == b"EMMC_BOOT" and self.read_pmt is not None:
            partdata, partentries = self.read_pmt()
            if partdata == b"":
                return None, None
            else:
                return partdata, partentries
        elif data[:8] == b"UFS_BOOT" and self.read_pmt is not None:
            partdata, partentries = self.read_pmt()
            if partdata == b"":
                return None, None
            else:
                return partdata, partentries
        if data == b"":
            return None, None
        guid_gpt = gpt(
            num_part_entries=gpt_settings.gpt_num_part_entries,
            part_entry_size=gpt_settings.gpt_part_entry_size,
            part_entry_start_lba=gpt_settings.gpt_part_entry_start_lba,
        )
        header = guid_gpt.parseheader(data, self.config.pagesize)
        if header.signature == b'\x00\x00\x00\x00\x00\x00\x00\x00':
            data = self.readflash(addr=self.mtk.daloader.daconfig.flashsize-0x4000, length=2 * self.config.pagesize, filename="", parttype=parttype, display=False)
            header = guid_gpt.parseheader(data, self.config.pagesize)
            if header.signature == b'\x00\x00\x00\x00\x00\x00\x00\x00':
                return None, None
        sectors = header.first_usable_lba
        if sectors == 0:
            return None, None
        data = self.readflash(addr=0, length=sectors * self.config.pagesize, filename="",
                              parttype=parttype, display=False)
        if data == b"":
            return None, None
        guid_gpt.parse(data, self.config.pagesize)
        return data, guid_gpt

    def get_backup_gpt(self, lun, gpt_num_part_entries, gpt_part_entry_size, gpt_part_entry_start_lba, parttype="user"):
        data = self.readflash(addr=0, length=2 * self.config.pagesize, filename="", parttype=parttype, display=False)
        if data == b"":
            return None
        guid_gpt = gpt(
            num_part_entries=gpt_num_part_entries,
            part_entry_size=gpt_part_entry_size,
            part_entry_start_lba=gpt_part_entry_start_lba,
        )
        header = guid_gpt.parseheader(data, self.config.SECTOR_SIZE_IN_BYTES)
        sectors = header.first_usable_lba - 1
        data = self.readflash(addr=header.backup_lba * self.config.pagesize,
                              length=sectors * self.config.pagesize, filename="",
                              display=False)
        if data == b"":
            return None
        return data
