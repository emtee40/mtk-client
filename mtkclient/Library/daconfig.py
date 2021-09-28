#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 MIT License
import logging
import os
from struct import unpack
from mtkclient.Library.utils import LogBase, read_object, logsetup
from mtkclient.config.payloads import pathconfig
from mtkclient.config.brom_config import damodes

class Storage:
    MTK_DA_HW_STORAGE_NOR = 0
    MTK_DA_HW_STORAGE_NAND = 1
    MTK_DA_HW_STORAGE_EMMC = 2
    MTK_DA_HW_STORAGE_SDMMC = 3
    MTK_DA_HW_STORAGE_UFS = 4


class DaStorage:
    MTK_DA_STORAGE_EMMC = 0x1
    MTK_DA_STORAGE_SDMMC = 0x2
    MTK_DA_STORAGE_UFS = 0x30
    MTK_DA_STORAGE_NAND = 0x10
    MTK_DA_STORAGE_NAND_SLC = 0x11
    MTK_DA_STORAGE_NAND_MLC = 0x12
    MTK_DA_STORAGE_NAND_TLC = 0x13
    MTK_DA_STORAGE_NAND_AMLC = 0x14
    MTK_DA_STORAGE_NAND_SPI = 0x15
    MTK_DA_STORAGE_NOR = 0x20
    MTK_DA_STORAGE_NOR_SERIAL = 0x21
    MTK_DA_STORAGE_NOR_PARALLEL = 0x22


class EMMC_PartitionType:
    MTK_DA_EMMC_PART_BOOT1 = 1
    MTK_DA_EMMC_PART_BOOT2 = 2
    MTK_DA_EMMC_PART_RPMB = 3
    MTK_DA_EMMC_PART_GP1 = 4
    MTK_DA_EMMC_PART_GP2 = 5
    MTK_DA_EMMC_PART_GP3 = 6
    MTK_DA_EMMC_PART_GP4 = 7
    MTK_DA_EMMC_PART_USER = 8
    MTK_DA_EMMC_PART_END = 9
    MTK_DA_EMMC_BOOT1_BOOT2 = 10


class UFS_PartitionType:
    UFS_LU0 = 0
    UFS_LU1 = 1
    UFS_LU2 = 2
    UFS_LU3 = 3
    UFS_LU4 = 4
    UFS_LU5 = 5
    UFS_LU6 = 6
    UFS_LU7 = 7
    UFS_LU8 = 8


class Memory:
    M_EMMC = 1
    M_NAND = 2
    M_NOR = 3


class NandCellUsage:
    CELL_UNI = 0,
    CELL_BINARY = 1
    CELL_TRI = 2
    CELL_QUAD = 3
    CELL_PENTA = 4
    CELL_HEX = 5
    CELL_HEPT = 6
    CELL_OCT = 7


entry_region = [
    ('m_buf', 'I'),
    ('m_len', 'I'),
    ('m_start_addr', 'I'),
    ('m_start_offset', 'I'),
    ('m_sig_len', 'I')]

DA = [
    ('magic', 'H'),
    ('hw_code', 'H'),
    ('hw_sub_code', 'H'),
    ('hw_version', 'H'),
    ('sw_version', 'H'),
    ('reserved1', 'H'),
    ('pagesize', 'H'),
    ('reserved3', 'H'),
    ('entry_region_index', 'H'),
    ('entry_region_count', 'H')
    # vector<entry_region> LoadRegion
]


class DAconfig(metaclass=LogBase):
    def __init__(self, mtk, loader=None, preloader=None, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel)
        self.mtk = mtk
        self.pathconfig = pathconfig()
        self.config = self.mtk.config
        self.usbwrite = self.mtk.port.usbwrite
        self.usbread = self.mtk.port.usbread
        self.flashsize = 0
        self.flashtype = "emmc"
        self.sparesize = 0
        self.readsize = 0
        self.pagesize = 512
        self.da = None
        self.da2 = None
        self.dasetup = {}
        self.loader = loader
        self.extract_emi(preloader)

        if loader is None:
            loaders = []
            for root, dirs, files in os.walk(self.pathconfig.get_loader_path(), topdown=False):
                for file in files:
                    if "Preloader" not in root:
                        loaders.append(os.path.join(root, file))
            for loader in loaders:
                self.parse_da_loader(loader)
        else:
            if not os.path.exists(loader):
                self.warning("Couldn't open " + loader)
            else:
                self.parse_da_loader(loader)

    def m_extract_emi(self, data):
        idx = data.find(b"\x4D\x4D\x4D\x01\x38\x00\x00\x00")
        siglen = 0
        if idx != -1:
            data = data[idx:]
            mlen = unpack("<I", data[0x20:0x20 + 4])[0]
            siglen = unpack("<I", data[0x2C:0x2C + 4])[0]
            data = data[:mlen]

        idx = data.find(b"MTK_BLOADER_INFO")
        if idx == -1:
            return None
        elif idx == 0:
            return data
        emi = data[idx:-siglen]
        rlen = len(emi) - 4
        if len(emi) > 4:
            val = unpack("<I", emi[-4:])[0]
            if val == rlen:
                emi = emi[:rlen]
                if not self.config.chipconfig.damode==damodes.XFLASH:
                    if emi.find(b"MTK_BIN")!=-1:
                        emi=emi[emi.find(b"MTK_BIN")+0xC:]
                return emi
        return None

    def extract_emi(self, preloader=None) -> bytearray:
        if preloader is None:
            self.emi = None
            return b""
        if isinstance(preloader, bytearray) or isinstance(preloader, bytes):
            data = bytearray(preloader)
        elif isinstance(preloader, str):
            if os.path.exists(preloader):
                with open(preloader, "rb") as rf:
                    data = rf.read()
            else:
                assert "Preloader :"+preloader+" doesn't exist. Aborting."
                exit(1)
        self.emi = self.m_extract_emi(data)

    def parse_da_loader(self, loader):
        if not "MTK_AllInOne_DA" in loader:
            return True
        try:
            if loader not in self.dasetup:
                self.dasetup[loader] = []
            with open(loader, 'rb') as bootldr:
                # data = bootldr.read()
                # self.debug(hexlify(data).decode('utf-8'))
                bootldr.seek(0x68)
                count_da = unpack("<I", bootldr.read(4))[0]
                for i in range(0, count_da):
                    bootldr.seek(0x6C + (i * 0xDC))
                    datmp = read_object(bootldr.read(0x14), DA)  # hdr
                    datmp["loader"] = loader
                    da = [datmp]
                    # bootldr.seek(0x6C + (i * 0xDC) + 0x14) #sections
                    count = datmp["entry_region_count"]
                    for m in range(0, count):
                        entry_tmp = read_object(bootldr.read(20), entry_region)
                        da.append(entry_tmp)
                    self.dasetup[loader].append(da)
                return True
        except Exception as e:
            self.error("Couldn't open loader: " + loader + ". Reason: " + str(e))
        return False

    def setup(self):
        dacode = self.config.chipconfig.dacode
        for loader in self.dasetup:
            for setup in self.dasetup[loader]:
                if setup[0]["hw_code"] == dacode:
                    if setup[0]["hw_version"] <= self.config.hwver:
                        if setup[0]["sw_version"] <= self.config.swver:
                            if self.loader is None:
                                self.da = setup
                                self.loader = loader

        if self.da is None:
            self.error("No da config set up")
        return self.da
