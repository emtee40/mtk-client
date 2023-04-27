#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import logging
import os
import sys
import time
from struct import pack, unpack
from binascii import hexlify
from mtkclient.Library.utils import LogBase, logsetup, structhelper
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.daconfig import DaStorage, EMMC_PartitionType
from mtkclient.Library.partition import Partition
from mtkclient.config.payloads import pathconfig
from mtkclient.Library.legacy_ext import legacyext
from mtkclient.config.mtk_config import Mtk_Config
from queue import Queue
from threading import Thread

rq = Queue()

def writedata(filename, rq):
    pos = 0
    with open(filename, "wb") as wf:
        while True:
            data = rq.get()
            if data is None:
                break
            pos += len(data)
            wf.write(data)
            rq.task_done()

class norinfo:
    m_nor_ret = None
    m_nor_chip_select = None
    m_nor_flash_id = None
    m_nor_flash_size = None
    m_nor_flash_dev_code = None
    m_nor_flash_otp_status = None
    m_nor_flash_otp_size = None

    def __init__(self, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.m_nor_ret = sh.dword(True)
        self.m_nor_chip_select = sh.bytes(2)
        self.m_nor_flash_id = sh.short(True)
        self.m_nor_flash_size = sh.dword(True)
        self.m_nor_flash_dev_code = sh.shorts(4, True)
        self.m_nor_flash_otp_status = sh.dword(True)
        self.m_nor_flash_otp_size = sh.dword(True)

    def __repr__(self):
        res = f"m_nor_ret = {hex(self.m_nor_ret)}\n"
        res += f"m_nor_chip_select = {hexlify(self.m_nor_chip_select).decode('utf-8')}\n"
        res += f"m_nor_flash_id = {hex(self.m_nor_flash_id)}\n"
        res += f"m_nor_flash_size = {hex(self.m_nor_flash_size)}\n"
        val = pack("<HHHH", self.m_nor_flash_dev_code[0], self.m_nor_flash_dev_code[1], self.m_nor_flash_dev_code[2],
                   self.m_nor_flash_dev_code[3])
        res += f"m_nor_flash_dev_code = {hexlify(val).decode('utf-8')}\n"
        res += f"m_nor_flash_otp_status = {hex(self.m_nor_flash_otp_status)}\n"
        res += f"m_nor_flash_otp_size = {hex(self.m_nor_flash_otp_size)}\n"

        res += f"m_sdmmc_cid = {hexlify(val).decode('utf-8')}\n"
        return res

class norinfo_iot:
    m_nor_ret = None
    m_nor_chip_select = None
    m_nor_flash_id = None
    m_nor_flash_size = None
    m_nor_flash_dev_code = None
    m_nor_flash_otp_status = None
    m_nor_flash_otp_size = None

    def __init__(self, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.m_nor_ret = sh.dword(True)
        self.m_nor_chip_select = sh.bytes(2)
        self.m_nor_flash_id = sh.short(True)
        self.m_nor_flash_size = sh.dword(True)
        self.m_nor_flash_size_die1 = sh.dword(True)
        self.m_nor_flash_dev_code = sh.shorts(4, True)
        self.m_nor_flash_otp_status = sh.dword(True)
        self.m_nor_flash_otp_size = sh.dword(True)

        self.m_nor_flash_id_die2 = sh.short(True)
        self.m_nor_flash_size_die2 = sh.dword(True)
        self.m_nor_flash_dev_code_die2 = sh.shorts(4, True)
        self.m_nor_flash_otp_status_die2 = sh.dword(True)
        self.m_nor_flash_otp_size_die2 = sh.dword(True)

    def __repr__(self):
        res = f"m_nor_ret = {hex(self.m_nor_ret)}\n"
        res += f"m_nor_chip_select = {hexlify(self.m_nor_chip_select).decode('utf-8')}\n"
        res += f"m_nor_flash_id = {hex(self.m_nor_flash_id)}\n"
        res += f"m_nor_flash_size = {hex(self.m_nor_flash_size)}\n"
        val = pack("<HHHH", self.m_nor_flash_dev_code[0], self.m_nor_flash_dev_code[1], self.m_nor_flash_dev_code[2],
                   self.m_nor_flash_dev_code[3])
        res += f"m_nor_flash_dev_code = {hexlify(val).decode('utf-8')}\n"
        res += f"m_nor_flash_otp_status = {hex(self.m_nor_flash_otp_status)}\n"
        res += f"m_nor_flash_otp_size = {hex(self.m_nor_flash_otp_size)}\n"
        res += f"m_nor_flash_id_die2 = {hex(self.m_nor_flash_id)}\n"
        res += f"m_nor_flash_size_die2 = {hex(self.m_nor_flash_size)}\n"
        val = pack("<HHHH", self.m_nor_flash_dev_code[0], self.m_nor_flash_dev_code[1], self.m_nor_flash_dev_code[2],
                   self.m_nor_flash_dev_code[3])
        res += f"m_nor_flash_dev_code_die2 = {hexlify(val).decode('utf-8')}\n"
        res += f"m_nor_flash_otp_status_die2 = {hex(self.m_nor_flash_otp_status)}\n"
        res += f"m_nor_flash_otp_size_die2 = {hex(self.m_nor_flash_otp_size)}\n"
        return res

class nandinfo32:
    m_nand_info = None
    m_nand_chip_select = None
    m_nand_flash_id = None
    m_nand_flash_size = None
    m_nand_flash_id_count = None
    info2 = None

    def __init__(self, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.m_nand_info = sh.dword(True)
        self.m_nand_chip_select = sh.bytes()
        self.m_nand_flash_id = sh.short(True)
        self.m_nand_flash_size = sh.dword(True)
        self.m_nand_flash_id_count = sh.short(True)
        self.info2 = None

    def __repr__(self):
        res = f"m_nand_info = {hex(self.m_nand_info)}\n"
        res += f"m_nand_chip_select = {hex(self.m_nand_chip_select)}\n"
        res += f"m_nand_flash_id = {hex(self.m_nand_flash_id)}\n"
        res += f"m_nand_flash_size = {hex(self.m_nand_flash_size)}\n"
        res += f"m_nand_flash_id_count = {hex(self.m_nand_flash_id_count)}\n"
        return res


class nandinfo_iot:
    m_nand_info = None
    m_nand_chip_select = None
    m_nand_flash_id = None
    m_nand_flash_size = None
    m_nand_flash_id_count = None
    info2 = None

    def __init__(self, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.m_nand_info = sh.dword(True)
        self.m_nand_chip_select = sh.bytes()
        self.m_nand_flash_id = sh.short(True)
        self.m_nand_flash_size = sh.dword(True)
        self.m_nand_flash_dev_code = sh.shorts(4, True)
        self.m_nand_flash_dev_code_part2 = sh.shorts(4, True)
        self.m_nand_pagesize = sh.short()
        self.m_nand_sparesize = sh.short()
        self.m_nand_pages_per_block = sh.short()
        self.m_nand_io_interface = sh.bytes()
        self.m_nand_addr_cycle = sh.bytes()
        self.info2 = None

    def __repr__(self):
        res = f"m_nand_info = {hex(self.m_nand_info)}\n"
        res += f"m_nand_chip_select = {hex(self.m_nand_chip_select)}\n"
        res += f"m_nand_flash_id = {hex(self.m_nand_flash_id)}\n"
        res += f"m_nand_flash_size = {hex(self.m_nand_flash_size)}\n"
        val = pack("<HHHH", self.m_nand_flash_dev_code[0], self.m_nand_flash_dev_code[1], self.m_nand_flash_dev_code[2],
                   self.m_nand_flash_dev_code[3])
        res += f"m_nand_flash_dev_code = {hexlify(val).decode('utf-8')}\n"
        val = pack("<HHHH", self.m_nand_flash_dev_code_part2[0], self.m_nand_flash_dev_code_part2[1], self.m_nand_flash_dev_code_part2[2],
                   self.m_nand_flash_dev_code_part2[3])
        res += f"m_nand_flash_dev_code_part2 = {hexlify(val).decode('utf-8')}\n"
        res += f"m_nand_pagesize = {hex(self.m_nand_pagesize)}\n"
        res += f"m_nand_sparesize = {hex(self.m_nand_sparesize)}\n"
        res += f"m_nand_pages_per_block = {hex(self.m_nand_pages_per_block)}\n"
        res += f"m_nand_io_interface = {hex(self.m_nand_io_interface)}\n"
        res += f"m_nand_addr_cycle = {hex(self.m_nand_addr_cycle)}\n"
        return res

class nandinfo64:
    m_nand_info = None
    m_nand_chip_select = None
    m_nand_flash_id = None
    m_nand_flash_size = None
    m_nand_flash_id_count = None
    info2 = None

    def __init__(self, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.m_nand_info = sh.dword(True)
        self.m_nand_chip_select = sh.bytes()
        self.m_nand_flash_id = sh.short(True)
        self.m_nand_flash_size = sh.qword(True)
        self.m_nand_flash_id_count = sh.short(True)
        self.info2 = None

    def __repr__(self):
        res = f"m_nand_info = {hex(self.m_nand_info)}\n"
        res += f"m_nand_chip_select = {hex(self.m_nand_chip_select)}\n"
        res += f"m_nand_flash_id = {hex(self.m_nand_flash_id)}\n"
        res += f"m_nand_flash_size = {hex(self.m_nand_flash_size)}\n"
        res += f"m_nand_flash_id_count = {hex(self.m_nand_flash_id_count)}\n"
        return res


# ('m_nand_flash_dev_code', '>7H'),

class nandinfo2:
    m_nand_pagesize = None
    m_nand_sparesize = None
    m_nand_pages_per_block = None
    m_nand_io_interface = None
    m_nand_addr_cycle = None
    m_nand_bmt_exist = None

    def __init__(self, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.m_nand_pagesize = sh.short(True)
        self.m_nand_sparesize = sh.short(True)
        self.m_nand_pages_per_block = sh.short(True)
        self.m_nand_io_interface = sh.bytes()
        self.m_nand_addr_cycle = sh.bytes()
        self.m_nand_bmt_exist = sh.bytes()

    def __repr__(self):
        res = f"m_nand_pagesize = {hex(self.m_nand_pagesize)}\n"
        res += f"m_nand_sparesize = {hex(self.m_nand_sparesize)}\n"
        res += f"m_nand_pages_per_block = {hex(self.m_nand_pages_per_block)}\n"
        res += f"m_nand_io_interface = {hex(self.m_nand_io_interface)}\n"
        res += f"m_nand_addr_cycle = {hex(self.m_nand_addr_cycle)}\n"
        res += f"m_nand_bmt_exist = {hex(self.m_nand_bmt_exist)}\n"
        return res


class emmcinfo:
    m_emmc_ret = None
    m_emmc_boot1_size = None
    m_emmc_boot2_size = None
    m_emmc_rpmb_size = None
    m_emmc_gp_size = None
    m_emmc_ua_size = None
    m_emmc_cid = None
    m_emmc_fwver = None

    def __init__(self, config: Mtk_Config, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.config = config
        self.m_emmc_ret = sh.dword(True)
        self.m_emmc_boot1_size = sh.qword(True)
        self.m_emmc_boot2_size = sh.qword(True)
        self.m_emmc_rpmb_size = sh.qword(True)
        self.m_emmc_gp_size = sh.qwords(4, True)
        self.m_emmc_ua_size = sh.qword(True)
        self.m_emmc_cid = sh.qwords(2, True)
        self.m_emmc_fwver = sh.bytes(8)

    def __repr__(self):
        res = f"m_emmc_ret = {hex(self.m_emmc_ret)}\n"
        res += f"m_emmc_boot1_size = {hex(self.m_emmc_boot1_size)}\n"
        res += f"m_emmc_boot2_size = {hex(self.m_emmc_boot2_size)}\n"
        res += f"m_emmc_rpmb_size = {hex(self.m_emmc_rpmb_size)}\n"
        res += f"m_emmc_gp_size[0] = {hex(self.m_emmc_gp_size[0])}\n"
        res += f"m_emmc_gp_size[1] = {hex(self.m_emmc_gp_size[1])}\n"
        res += f"m_emmc_gp_size[2] = {hex(self.m_emmc_gp_size[2])}\n"
        res += f"m_emmc_gp_size[3] = {hex(self.m_emmc_gp_size[3])}\n"
        res += f"m_emmc_ua_size = {hex(self.m_emmc_ua_size)}\n"
        cid = pack("<QQ", self.m_emmc_cid[0], self.m_emmc_cid[1])
        res += f"m_emmc_cid = {hexlify(cid).decode('utf-8')}\n"
        if self.config.hwparam is not None:
            self.config.set_cid(cid)
        res += f"m_emmc_fwver = {hexlify(self.m_emmc_fwver).decode('utf-8')}\n"
        return res


class emmcinfo_iot:
    m_emmc_ret = None
    m_emmc_boot1_size = None
    m_emmc_boot2_size = None
    m_emmc_rpmb_size = None
    m_emmc_gp_size = None
    m_emmc_ua_size = None
    m_emmc_cid = None
    m_emmc_fwver = None

    def __init__(self, config: Mtk_Config, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.config = config
        self.m_emmc_ret = sh.dword(True)
        self.m_emmc_manufacturer_id = sh.bytes()
        self.m_emmc_product_name = sh.bytes(6)
        self.m_emmc_partitioned = sh.bytes()
        self.m_emmc_boot1_size = sh.dword(True)
        self.m_emmc_boot2_size = sh.dword(True)
        self.m_emmc_rpmb_size = sh.dword(True)
        self.m_emmc_gp_size = sh.dwords(4, True)
        self.m_emmc_ua_size = sh.dword(True)

    def __repr__(self):
        res = f"m_emmc_ret = {hex(self.m_emmc_ret)}\n"
        res += f"m_emmc_manufacturer_id = {hex(self.m_emmc_manufacturer_id)}\n"
        res += f"m_emmc_product_name = {self.m_emmc_product_name.hex()}\n"
        res += f"m_emmc_partitioned = {hex(self.m_emmc_partitioned)}\n"
        res += f"m_emmc_boot1_size = {hex(self.m_emmc_boot1_size)}\n"
        res += f"m_emmc_boot2_size = {hex(self.m_emmc_boot2_size)}\n"
        res += f"m_emmc_rpmb_size = {hex(self.m_emmc_rpmb_size)}\n"
        res += f"m_emmc_gp_size[0] = {hex(self.m_emmc_gp_size[0])}\n"
        res += f"m_emmc_gp_size[1] = {hex(self.m_emmc_gp_size[1])}\n"
        res += f"m_emmc_gp_size[2] = {hex(self.m_emmc_gp_size[2])}\n"
        res += f"m_emmc_gp_size[3] = {hex(self.m_emmc_gp_size[3])}\n"
        res += f"m_emmc_ua_size = {hex(self.m_emmc_ua_size)}\n"
        return res

class sdcinfo:
    m_sdmmc_info = None
    m_sdmmc_ua_size = None
    m_sdmmc_cid = None

    def __init__(self, config: Mtk_Config, data=None):
        if data is None:
            return
        sh = structhelper(data)
        self.config = config
        self.m_sdmmc_info = sh.dword(True)
        self.m_sdmmc_ua_size = sh.qword(True)
        self.m_sdmmc_cid = sh.qwords(2, True)

    def __repr__(self):
        print(f"m_sdmmc_info = {hex(self.m_sdmmc_info)}")
        print(f"m_sdmmc_ua_size = {hex(self.m_sdmmc_ua_size)}")
        cid = pack("<QQ", self.m_sdmmc_cid[0], self.m_sdmmc_cid[1])
        if self.config.hwparam is not None:
            self.config.set_cid(cid)
        print(f"m_sdmmc_cid = {hexlify(cid).decode('utf-8')}")


class configinfo:
    m_int_sram_ret = None
    m_int_sram_size = None
    m_ext_ram_ret = None
    m_ext_ram_type = None
    m_ext_ram_chip_select = None
    m_ext_ram_size = None
    randomid = None

    def __init__(self, data):
        sh = structhelper(data)
        self.m_int_sram_ret = sh.dword(True)
        self.m_int_sram_size = sh.dword(True)
        self.m_ext_ram_ret = sh.dword(True)
        self.m_ext_ram_type = sh.bytes()
        self.m_ext_ram_chip_select = sh.bytes()
        self.m_ext_ram_size = sh.qword(True)
        self.randomid = sh.qwords(2, True)

    def __repr__(self):
        res = "m_int_sram_ret = 0x%X\n" % self.m_int_sram_ret
        res += "m_int_sram_size = 0x%X\n" % self.m_int_sram_size
        res += "m_ext_ram_ret = 0x%X\n" % self.m_ext_ram_ret
        res += "m_ext_ram_type = 0x%X\n" % self.m_ext_ram_type
        res += "m_ext_ram_chip_select = 0x%X\n" % self.m_ext_ram_chip_select
        res += "m_int_sram_ret = 0x%X\n" % self.m_int_sram_ret
        res += f"m_ext_ram_size = {hex(self.m_ext_ram_size)}\n"
        res += "randomid = 0x%X%X\n" % (self.randomid[0], self.randomid[1])
        return res

class configinfo_iot:
    m_int_sram_ret = None
    m_int_sram_size = None
    m_ext_ram_ret = None
    m_ext_ram_type = None
    m_ext_ram_chip_select = None
    m_ext_ram_size = None

    def __init__(self, data):
        sh = structhelper(data)
        self.m_int_sram_ret = sh.dword(True)
        self.m_int_sram_size = sh.dword(True)
        self.m_ext_ram_ret = sh.dword(True)
        self.m_ext_ram_type = sh.bytes()
        self.m_ext_ram_chip_select = sh.bytes()
        self.m_ext_ram_size = sh.dword(True)
        self.sf_candidate = sh.bytes(12)

    def __repr__(self):
        res = "m_int_sram_ret = 0x%X\n" % self.m_int_sram_ret
        res += "m_int_sram_size = 0x%X\n" % self.m_int_sram_size
        res += "m_ext_ram_ret = 0x%X\n" % self.m_ext_ram_ret
        res += "m_ext_ram_type = 0x%X\n" % self.m_ext_ram_type
        res += "m_ext_ram_chip_select = 0x%X\n" % self.m_ext_ram_chip_select
        res += "m_int_sram_ret = 0x%X\n" % self.m_int_sram_ret
        res += f"m_ext_ram_size = {hex(self.m_ext_ram_size)}\n"
        res += f"sf_candidate = {self.sf_candidate.hex()}\n"
        return res

class passinfo:
    ack = None
    m_download_status = None
    m_boot_style = None
    soc_ok = None

    def __init__(self, data):
        sh = structhelper(data)
        self.ack = sh.bytes()
        self.m_download_status = sh.dword(True)
        self.m_boot_style = sh.dword(True)
        self.soc_ok = sh.bytes()


def crc_word(data, chs=0):
    return (sum(data) + chs) & 0xFFFF


errortbl = {
    3000: "S_DA_INT_RAM_ERROR",
    3001: "S_DA_EXT_RAM_ERROR",
    3002: "S_DA_SETUP_DRAM_FAIL",
    3003: "S_DA_SETUP_PLL_ERR",
    3004: "S_DA_DRAM_NOT_SUPPORT",
    3005: "S_DA_RAM_FLOARTING",
    3006: "S_DA_RAM_UNACCESSABLE",
    3007: "S_DA_RAM_ERROR",
    3008: "S_DA_DEVICE_NOT_FOUND",
    3009: "S_DA_NOR_UNSUPPORTED_DEV_ID",
    3010: "S_DA_NAND_UNSUPPORTED_DEV_ID",
    3011: "S_DA_NOR_FLASH_NOT_FOUND",
    3012: "S_DA_NAND_FLASH_NOT_FOUND",
    3013: "S_DA_SOC_CHECK_FAIL",
    3014: "S_DA_NOR_PROGRAM_FAILED",
    3015: "S_DA_NOR_ERASE_FAILED",
    3016: "S_DA_NAND_PAGE_PROGRAM_FAILED",
    3017: "S_DA_NAND_SPARE_PROGRAM_FAILED",
    3018: "S_DA_NAND_HW_COPYBACK_FAILED",
    3019: "S_DA_NAND_ERASE_FAILED",
    3020: "S_DA_TIMEOUT",
    3021: "S_DA_IN_PROGRESS",
    3022: "S_DA_SUPERAND_ONLY_SUPPORT_PAGE_READ",
    3023: "S_DA_SUPERAND_PAGE_READ_NOT_SUPPORT",
    3024: "S_DA_SUPERAND_PAGE_PRGRAM_NOT_SUPPORT",
    3025: "S_DA_SUPERAND_SPARE_PRGRAM_NOT_SUPPORT",
    3026: "S_DA_SUPERAND_SPARE_READ_NOT_SUPPORT",
    3027: "S_DA_SUPERAND_PAGE_SPARE_PRGRAM_NOT_SUPPORT",
    3028: "S_DA_SUPERAND_COPYBACK_NOT_SUPPORT",
    3029: "S_DA_NOR_CMD_SEQUENCE_ERR",
    3030: "S_DA_NOR_BLOCK_IS_LOCKED",
    3031: "S_DA_NAND_BLOCK_IS_LOCKED",
    3032: "S_DA_NAND_BLOCK_DATA_UNSTABLE",
    3033: "S_DA_NOR_BLOCK_DATA_UNSTABLE",
    3034: "S_DA_NOR_VPP_RANGE_ERR",
    3035: "S_DA_INVALID_BEGIN_ADDR",
    3036: "S_DA_NOR_INVALID_ERASE_BEGIN_ADDR",
    3037: "S_DA_NOR_INVALID_READ_BEGIN_ADDR",
    3038: "S_DA_NOR_INVALID_PROGRAM_BEGIN_ADDR",
    3039: "S_DA_INVALID_RANGE",
    3040: "S_DA_NOR_PROGRAM_AT_ODD_ADDR",
    3041: "S_DA_NOR_PROGRAM_WITH_ODD_LENGTH",
    3042: "S_DA_NOR_BUFPGM_NO_SUPPORT",
    3043: "S_DA_NAND_UNKNOWN_ERR",
    3044: "S_DA_NAND_BAD_BLOCK",
    3045: "S_DA_NAND_ECC_1BIT_CORRECT",
    3046: "S_DA_NAND_ECC_2BITS_ERR",
    3047: "S_DA_NAND_ECC_UNCORRECTABLE_ERROR",
    3048: "S_DA_NAND_SPARE_CHKSUM_ERR",
    3049: "S_DA_NAND_HW_COPYBACK_DATA_INCONSISTENT",
    3050: "S_DA_NAND_INVALID_PAGE_INDEX",
    3051: "S_DA_NFI_NOT_SUPPORT",
    3052: "S_DA_NFI_CS1_NOT_SUPPORT",
    3053: "S_DA_NFI_16BITS_IO_NOT_SUPPORT",
    3054: "S_DA_NFB_BOOTLOADER_NOT_EXIST",
    3055: "S_DA_NAND_NO_GOOD_BLOCK",
    3056: "S_DA_BOOTLOADER_IS_TOO_LARGE",
    3057: "S_DA_SIBLEY_REWRITE_OBJ_MODE_REGION",
    3058: "S_DA_SIBLEY_WRITE_B_HALF_IN_CTRL_MODE_REGION",
    3059: "S_DA_SIBLEY_ILLEGAL_CMD",
    3060: "S_DA_SIBLEY_PROGRAM_AT_THE_SAME_REGIONS",
    3061: "S_DA_UART_GET_DATA_TIMEOUT",
    3062: "S_DA_UART_GET_CHKSUM_LSB_TIMEOUT",
    3063: "S_DA_UART_GET_CHKSUM_MSB_TIMEOUT",
    3064: "S_DA_UART_DATA_CKSUM_ERROR",
    3065: "S_DA_UART_RX_BUF_FULL",
    3066: "S_DA_FLASH_RECOVERY_BUF_NOT_ENOUGH",
    3067: "S_DA_HANDSET_SEC_INFO_NOT_FOUND",
    3068: "S_DA_HANDSET_SEC_INFO_MAC_VERIFY_FAIL",
    3069: "S_DA_HANDSET_ROM_INFO_NOT_FOUND",
    3070: "S_DA_HANDSET_FAT_INFO_NOT_FOUND",
    3071: "S_DA_OPERATION_UNSUPPORT_FOR_NFB",
    3072: "S_DA_BYPASS_POST_PROCESS",
    3073: "S_DA_NOR_OTP_NOT_SUPPORT",
    3074: "S_DA_NOR_OTP_EXIST",
    3075: "S_DA_NOR_OTP_LOCKED",
    3076: "S_DA_NOR_OTP_GETSIZE_FAIL",
    3077: "S_DA_NOR_OTP_READ_FAIL",
    3078: "S_DA_NOR_OTP_PROGRAM_FAIL",
    3079: "S_DA_NOR_OTP_LOCK_FAIL",
    3080: "S_DA_NOR_OTP_LOCK_CHECK_STATUS_FAIL",
    3081: "S_DA_BLANK_FLASH",
    3082: "S_DA_CODE_AREA_IS_BLANK",
    3083: "S_DA_SEC_RO_AREA_IS_BLANK",
    3084: "S_DA_NOR_OTP_UNLOCKED",
    3085: "S_DA_UNSUPPORTED_BBCHIP",
    3086: "S_DA_FAT_NOT_EXIST",
    3087: "S_DA_EXT_SRAM_NOT_FOUND",
    3088: "S_DA_EXT_DRAM_NOT_FOUND",
    3089: "S_DA_MT_PIN_LOW",
    3090: "S_DA_MT_PIN_HIGH",
    3091: "S_DA_MT_PIN_SHORT",
    3092: "S_DA_MT_BUS_ERROR",
    3093: "S_DA_MT_ADDR_NOT_2BYTE_ALIGNMENT",
    3094: "S_DA_MT_ADDR_NOT_4BYTE_ALIGNMENT",
    3095: "S_DA_MT_SIZE_NOT_2BYTE_ALIGNMENT",
    3096: "S_DA_MT_SIZE_NOT_4BYTE_ALIGNMENT",
    3097: "S_DA_MT_DEDICATED_PATTERN_ERROR",
    3098: "S_DA_MT_INC_PATTERN_ERROR",
    3099: "S_DA_MT_DEC_PATTERN_ERROR",
    3100: "S_DA_NFB_BLOCK_0_IS_BAD",
    3101: "S_DA_CUST_PARA_AREA_IS_BLANK",
    3102: "S_DA_ENTER_RELAY_MODE_FAIL",
    3103: "S_DA_ENTER_RELAY_MODE_IS_FORBIDDEN_AFTER_META",
    3104: "S_DA_NAND_PAGE_READ_FAILED",
    3105: "S_DA_NAND_IMAGE_BLOCK_NO_EXIST",
    3106: "S_DA_NAND_IMAGE_LIST_NOT_EXIST",
    3107: "S_DA_MBA_RESOURCE_NO_EXIST_IN_TARGET",
    3108: "S_DA_MBA_PROJECT_VERSION_NO_MATCH_WITH_TARGET",
    3109: "S_DA_MBA_UPDATING_RESOURCE_NO_EXIST_IN_TARGET",
    3110: "S_DA_MBA_UPDATING_RESOURCE_SIZE_EXCEED_IN_TARGET",
    3111: "S_DA_NAND_BIN_SIZE_EXCEED_MAX_SIZE",
    3112: "S_DA_NAND_EXCEED_CONTAINER_LIMIT",
    3113: "S_DA_NAND_REACH_END_OF_FLASH",
    3114: "S_DA_NAND_OTP_NOT_SUPPORT",
    3115: "S_DA_NAND_OTP_EXIST",
    3116: "S_DA_NAND_OTP_LOCKED",
    3117: "S_DA_NAND_OTP_LOCK_FAIL",
    3118: "S_DA_NAND_OTP_UNLOCKED",
    3119: "S_DA_OTP_NOT_SUPPORT",
    3120: "S_DA_OTP_EXIST",
    3121: "S_DA_OTP_LOCKED",
    3122: "S_DA_OTP_GETSIZE_FAIL",
    3123: "S_DA_OTP_READ_FAIL",
    3124: "S_DA_OTP_PROGRAM_FAIL",
    3125: "S_DA_OTP_LOCK_FAIL",
    3126: "S_DA_OTP_LOCK_CHECK_STATUS_FAIL",
    3127: "S_DA_OTP_UNLOCKED",
    3128: "S_DA_SEC_RO_ILLEGAL_MAGIC_TAIL",
    3129: "S_DA_HANDSET_FOTA_INFO_NOT_FOUND",
    3130: "S_DA_HANDSET_UA_INFO_NOT_FOUND",
    3131: "S_DA_SB_FSM_INVALID_INFO",
    3132: "S_DA_NFB_TARGET_DUAL_BL_PAIRED_VERSION_NOT_MATCHED_WITH_MAUI",
    3133: "S_DA_NFB_TARGET_DUAL_BL_FEATURE_COMBINATION_NOT_MATCHED_WITH_MAUI",
    3134: "S_DA_NFB_TARGET_IS_SINGLE_BL_BUT_PC_NOT",
    3135: "S_DA_NFB_TARGET_IS_DUAL_BL_BUT_PC_NOT",
    3136: "S_DA_NOR_TARGET_BL_PAIRED_VERSION_NOT_MATCHED_WITH_MAUI",
    3137: "S_DA_NOR_TARGET_BL_FEATURE_COMBINATION_NOT_MATCHED_WITH_MAUI",
    3138: "S_DA_NOR_TARGET_IS_NOT_NEW_BL_BUT_PC_IS",
    3139: "S_DA_NOR_TARGET_IS_NEW_BL_BUT_PC_NOT",
    3140: "S_DA_GEN_DA_VERSION_INFO_TEMP_ILB_FAIL",
    3141: "S_DA_FLASH_NOT_FOUND",
    3142: "S_DA_BOOT_CERT_NOT_EXIST",
    3143: "S_DA_NAND_CODE_IMAGE_OVERLAP_FAT_REGION",
    3144: "S_DA_DOWNLOAD_BOOTLOADER_FLASH_DEV_IS_NONE",
    3145: "S_DA_DOWNLOAD_BOOTLOADER_FLASH_DEV_IS_NOT_SUPPORTED",
    3146: "S_DA_DOWNLOAD_BOOTLOADER_BEGIN_ADDR_OVERLAPS_WITH_PREVIOUS_BOUNDARY",
    3147: "S_DA_UPDATE_BOOTLOADER_EXIST_MAGIC_NOT_MATCHED",
    3148: "S_DA_UPDATE_BOOTLOADER_FILE_TYPE_NOT_MATCHED",
    3149: "S_DA_UPDATE_BOOTLOADER_FILE_SIZE_EXCEEDS_BOUNDARY_ADDR",
    3150: "S_DA_UPDATE_BOOTLOADER_BEGIN_ADDR_NOT_MATCHED",
    3151: "S_DA_CBR_SET_BUF_AND_API_FAIL",
    3152: "S_DA_CBR_NOT_FOUND",
    3153: "S_DA_CBR_FLASH_LAYOUT_NOT_FOUND",
    3154: "S_DA_CBR_FLASH_SPACE_INFO_NOT_FOUND",
    3155: "S_DA_CBR_FLASH_CONFIG_NOT_FOUND",
    3156: "S_DA_CBR_SET_ENVRIONMENT_FAILED",
    3157: "S_DA_CBR_CREAT_FAILED",
    3158: "S_DA_CBR_COMPARE_FAILED",
    3159: "S_DA_CBR_WRONG_VERSION",
    3160: "S_DA_CBR_ALREADY_EXIST",
    3161: "S_DA_CBR_RECORD_BUF_TOO_SMALL",
    3162: "S_DA_CBR_RECORD_NOT_EXIST",
    3163: "S_DA_CBR_RECORD_ALREADY_EXIST",
    3164: "S_DA_CBR_FULL",
    3165: "S_DA_CBR_RECORD_WRITE_LEN_INCONSISTENT",
    3166: "S_DA_CBR_VERSION_NOT_MATCHED",
    3167: "S_DA_CBR_NOT_SUPPORT_PCT_FLASH",
    3168: "S_DA_CBR_UNKNOWN_ERROR",
    3169: "S_DA_SEC_RO_ACC_PARSE_ERROR",
    3170: "S_DA_HEADER_BLOCK_NOT_EXIST",
    3171: "S_DA_S_PRE_PARSE_CUSTOMER_NAME_FAIL",
    3172: "S_DA_S_RETRIEVE_SEC_RO_FAIL_IN_SECURE_INIT",
    3173: "S_DA_S_FLASH_INFO_NOT_EXIST",
    3174: "S_DA_S_MAUI_INFO_NOT_EXIST",
    3175: "S_DA_S_BOOTLOADER_SHARE_DATA_NOT_EXIST",
    3176: "S_DA_GFH_FILE_INFO_RETREIVAL_FAIL",
    3177: "S_DA_NAND_REMARK_FAIL",
    3178: "S_DA_TARGET_IS_NOT_NEW_BL_BUT_PC_IS",
    3179: "S_DA_EMMC_FLASH_NOT_FOUND",
    3180: "S_DA_EMMC_ENABLE_BOOT_FAILED",
    3181: "S_DA_HB_FOUND_IN_OTHER_FLASH_DEV",
    3182: "S_DA_USB_2_0_NOT_SUPPORT",
    3183: "S_DA_CBR_INIT_FAILED",
    3184: "S_DA_CBR_MAUI_INFO_SIZE_TOO_BIG",
    3185: "S_DA_CBR_WRITE_MAUI_INFO_FAILED",
    3186: "S_DA_CBR_READ_MAUI_INFO_FAILED",
    3187: "S_DA_UNSUPPORTED_OPERATION",
    3188: "S_DA_MBA_RESOURCE_BIN_NUMBER_NOT_MATCH_WITH_TARGET",
    3189: "S_DA_MBA_HEADER_NOT_EXIST",
    3190: "S_DA_MBA_RESOURCE_VERSION_NO_MATCH_WITH_TARGET",
    3191: "S_DA_BOOTLOADER_SELF_UPDATE_FAIL",
    3192: "S_DA_SEARCH_BL_SELF_UPDATE_INFO_FAIL",
    3193: "S_DA_SPACE_NOT_ENOUGH_FOR_EXT_BL_MARKER",
    3194: "S_DA_FIND_EXT_BL_MARKER_FAIL",
    3195: "S_DA_TOO_MANY_BAD_BLOCKS_FOR_EXT_BL_MARKER",
    3196: "S_DA_TOO_MANY_BAD_BLOCKS_FOR_EXT_BL_BACKUP",
    3197: "S_DA_EXT_BL_VER_MISMATCHED",
    3198: "S_DA_EXT_BL_VER_NOT_FOUND",
    3199: "S_DA_BL_SELF_UPDATE_FEATURE_CHECK_FAILED",
    3200: "S_DA_BL_ROM_INFO_NOT_FOUND",
    3201: "S_DA_EXT_BL_MAX_SIZE_MISMATCHED",
    3202: "S_DA_INVALID_PARAMETER_FROM_PC",
    3203: "S_DA_BL_SELF_UPDATE_NOT_SUPPORTED",
    3204: "S_DA_EXT_BL_HDR_NOT_FOUND",
    3205: "S_DA_S_FLASH_LAYOUT_NOT_EXIST",
    3206: "S_DA_S_FLASH_ID_NOT_EXIST",
    3207: "S_DA_MAUI_GFH_FLASH_ID_NOT_MATCH_WITH_TARGET",
    3208: "S_DA_FLASH_ERASE_SIZE_NOT_SUPPORT",
    3209: "S_DA_SRD_NOT_FOUND",
    3210: "S_DA_SRD_UPDATE_FAILED",
    3211: "S_DA_NAND_DATA_ADDR_NOT_PAGE_ALIGNMENT",
    3212: "S_DA_BL_GFH_BROM_SEC_CFG_NOT_FOUND",
    3213: "S_DA_BL_CUSTOMER_NAME_BUFFER_INSUFFICIENT",
    3214: "S_DA_COM_BUSY",
    3215: "S_DA_INITIAL_BMT_FAILED_CAUSED_FROM_POOL_SIZE_ERROR",
    3216: "S_DA_LOAD_ORIGINAL_BMT_FAILED",
    3217: "S_DA_INVALID_NAND_PAGE_BUFFER",
    3218: "S_DA_DL_BOOT_REGION_IS_OVERLAP_CONTROL_BLOCK_REGION",
    3219: "S_DA_PRE_DL_HB_INIT_FAIL",
    3220: "S_DA_POST_DL_HB_WRITE_FAIL",
    3221: "S_DA_LOAD_IMG_PARA_FAIL",
    3222: "S_DA_WRITE_IMG_PARA_FAIL",
    3223: "S_DA_UPDATE_HB_FAIL",
    3224: "S_DA_BIN_SIZE_EXCEED_MAX_ERR",
    3225: "S_DA_PARTIAL_BIN_TYPE_ERR",
    3226: "S_DA_IMAGE_PARA_QUERY_ERR",
    3227: "S_DA_IMAGE_PARA_UPDATE_ERR",
    3228: "S_DA_FLASH_LAYOUT_BIN_NOT_FOUND",
    3229: "S_DA_FLASH_LAYOUT_GET_ELEMENT_FAIL",
    3230: "S_DA_FLASH_LAYOUT_ADD_ELEMENT_FAIL",
    3231: "S_DA_CBR_FOUND_BUT_MAUI_NOT_EXIST",
    3232: "S_DA_UPDATE_BOOTLOADER_NOT_CONTAIN_CRITICAL_DATA",
    3233: "S_DA_DUMP_FLASH_LAYOUT_FAIL",
    3234: "S_DA_BMT_NO_INIT",
    3235: "S_DA_NOR_PROGRAM_REGION_IS_OVERLAP"
}


def error_to_string(errorcode):
    if errorcode in errortbl:
        return errortbl[errorcode]


class DALegacy(metaclass=LogBase):
    class Rsp:
        SOC_OK = b"\xC1"
        SOC_FAIL = b"\xCF"
        SYNC_CHAR = b"\xC0"
        CONT_CHAR = b"\x69"
        STOP_CHAR = b"\x96"
        ACK = b"\x5A"
        NACK = b"\xA5"
        UNKNOWN_CMD = b"\xBB"

    class PortValues:
        UART_BAUD_921600 = b'\x01',
        UART_BAUD_460800 = b'\x02',
        UART_BAUD_230400 = b'\x03',
        UART_BAUD_115200 = b'\x04',
        UART_BAUD_57600 = b'\x05',
        UART_BAUD_38400 = b'\x06',
        UART_BAUD_19200 = b'\x07',
        UART_BAUD_9600 = b'\x08',
        UART_BAUD_4800 = b'\x09',
        UART_BAUD_2400 = b'\x0a',
        UART_BAUD_1200 = b'\x0b',
        UART_BAUD_300 = b'\x0c',
        UART_BAUD_110 = b'\x0d'

    class Cmd:
        # COMMANDS
        DOWNLOAD_BLOADER_CMD = b"\x51"
        NAND_BMT_REMARK_CMD = b"\x52"

        SDMMC_SWITCH_PART_CMD = b"\x60"
        SDMMC_WRITE_IMAGE_CMD = b"\x61"
        SDMMC_WRITE_DATA_CMD = b"\x62"
        SDMMC_GET_CARD_TYPE = b"\x63"
        SDMMC_RESET_DIS_CMD = b"\x64"

        UFS_SWITCH_PART_CMD = b"\x80"
        UFS_WRITE_IMAGE_CMD = b"\x81"
        UFS_WRITE_DATA_CMD = b"\x82"
        UFS_READ_GPT_CMD = b"\x85"
        UFS_WRITE_GPT_CMD = b"\x89"

        UFS_OTP_CHECKDEVICE_CMD = b"\x8a"
        UFS_OTP_GETSIZE_CMD = b"\x8b"
        UFS_OTP_READ_CMD = b"\x8c"
        UFS_OTP_PROGRAM_CMD = b"\x8d"
        UFS_OTP_LOCK_CMD = b"\x8e"
        UFS_OTP_LOCK_CHECKSTATUS_CMD = b"\x8f"

        USB_SETUP_PORT = b"\x70"
        USB_LOOPBACK = b"\x71"
        USB_CHECK_STATUS = b"\x72"
        USB_SETUP_PORT_EX = b"\x73"

        # EFUSE
        READ_REG32_CMD = b"\x7A"
        WRITE_REG32_CMD = b"\x7B"
        PWR_READ16_CMD = b"\x7C"
        PWR_WRITE16_CMD = b"\x7D"
        PWR_READ8_CMD = b"\x7E"
        PWR_WRITE8_CMD = b"\x7F"

        EMMC_OTP_CHECKDEVICE_CMD = b"\x99"
        EMMC_OTP_GETSIZE_CMD = b"\x9A"
        EMMC_OTP_READ_CMD = b"\x9B"
        EMMC_OTP_PROGRAM_CMD = b"\x9C"
        EMMC_OTP_LOCK_CMD = b"\x9D"
        EMMC_OTP_LOCK_CHECKSTATUS_CMD = b"\x9E"

        WRITE_USB_DOWNLOAD_CONTROL_BIT_CMD = b"\xA0"
        WRITE_PARTITION_TBL_CMD = b"\xA1"
        READ_PARTITION_TBL_CMD = b"\xA2"
        READ_BMT = b"\xA3"
        SDMMC_WRITE_PMT_CMD = b"\xA4"
        SDMMC_READ_PMT_CMD = b"\xA5"
        READ_IMEI_PID_SWV_CMD = b"\xA6"
        READ_DOWNLOAD_INFO = b"\xA7"
        WRITE_DOWNLOAD_INFO = b"\xA8"
        SDMMC_WRITE_GPT_CMD = b"\xA9"
        NOR_READ_PTB_CMD = b"\xAA"
        NOR_WRITE_PTB_CMD = b"\xAB"

        NOR_BLOCK_INDEX_TO_ADDRESS = b"\xB0"  # deprecated
        NOR_ADDRESS_TO_BLOCK_INDEX = b"\xB1"  # deprecated
        NOR_WRITE_DATA = b"\xB2"  # deprecated
        NAND_WRITE_DATA = b"\xB3"
        SECURE_USB_RECHECK_CMD = b"\xB4"
        SECURE_USB_DECRYPT_CMD = b"\xB5"
        NFB_BL_FEATURE_CHECK_CMD = b"\xB6"  # deprecated
        NOR_BL_FEATURE_CHECK_CMD = b"\xB7"  # deprecated

        SF_WRITE_IMAGE_CMD = b"\xB8"  # deprecated

        # Android S-USBDL
        SECURE_USB_IMG_INFO_CHECK_CMD = b"\xB9"
        SECURE_USB_WRITE = b"\xBA"
        SECURE_USB_ROM_INFO_UPDATE_CMD = b"\xBB"
        SECURE_USB_GET_CUST_NAME_CMD = b"\xBC"
        SECURE_USB_CHECK_BYPASS_CMD = b"\xBE"
        SECURE_USB_GET_BL_SEC_VER_CMD = b"\xBF"
        # Android S-USBDL

        VERIFY_IMG_CHKSUM_CMD = b"\xBD"

        GET_BATTERY_VOLTAGE_CMD = b"\xD0"
        POST_PROCESS = b"\xD1"
        SPEED_CMD = b"\xD2"
        MEM_CMD = b"\xD3"
        FORMAT_CMD = b"\xD4"
        WRITE_CMD = b"\xD5"
        READ_CMD = b"\xD6"
        WRITE_REG16_CMD = b"\xD7"
        READ_REG16_CMD = b"\xD8"
        FINISH_CMD = b"\xD9"
        GET_DSP_VER_CMD = b"\xDA"
        ENABLE_WATCHDOG_CMD = b"\xDB"
        NFB_WRITE_BLOADER_CMD = b"\xDC"  # deprecated
        NAND_IMAGE_LIST_CMD = b"\xDD"
        NFB_WRITE_IMAGE_CMD = b"\xDE"
        NAND_READPAGE_CMD = b"\xDF"
        CHK_PC_SEC_INFO_CMD = b"\xE0"
        UPDATE_FLASHTOOL_CFG_CMD = b"\xE1"
        CUST_PARA_GET_INFO_CMD = b"\xE2"  # deprecated
        CUST_PARA_READ_CMD = b"\xE3"  # deprecated
        CUST_PARA_WRITE_CMD = b"\xE4"  # deprecated
        SEC_RO_GET_INFO_CMD = b"\xE5"  # deprecated
        SEC_RO_READ_CMD = b"\xE6"  # deprecated
        SEC_RO_WRITE_CMD = b"\xE7"  # deprecated
        ENABLE_DRAM = b"\xE8"
        OTP_CHECKDEVICE_CMD = b"\xE9"
        OTP_GETSIZE_CMD = b"\xEA"
        OTP_READ_CMD = b"\xEB"
        OTP_PROGRAM_CMD = b"\xEC"
        OTP_LOCK_CMD = b"\xED"
        OTP_LOCK_CHECKSTATUS_CMD = b"\xEE"
        GET_PROJECT_ID_CMD = b"\xEF"
        GET_FAT_INFO_CMD = b"\xF0"  # deprecated
        FDM_MOUNTDEVICE_CMD = b"\xF1"
        FDM_SHUTDOWN_CMD = b"\xF2"
        FDM_READSECTORS_CMD = b"\xF3"
        FDM_WRITESECTORS_CMD = b"\xF4"
        FDM_MEDIACHANGED_CMD = b"\xF5"
        FDM_DISCARDSECTORS_CMD = b"\xF6"
        FDM_GETDISKGEOMETRY_CMD = b"\xF7"
        FDM_LOWLEVELFORMAT_CMD = b"\xF8"
        FDM_NONBLOCKWRITESECTORS_CMD = b"\xF9"
        FDM_RECOVERABLEWRITESECTORS_CMD = b"\xFA"
        FDM_RESUMESECTORSTATES = b"\xFB"
        NAND_EXTRACT_NFB_CMD = b"\xFC"  # deprecated
        NAND_INJECT_NFB_CMD = b"\xFD"  # deprecated

        MEMORY_TEST_CMD = b"\xFE"
        ENTER_RELAY_MODE_CMD = b"\xFF"

    def __init__(self, mtk, daconfig, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.debug = self.debug
        self.error = self.error
        self.info = self.info
        self.emmc = None
        self.nand = None
        self.nor = None
        self.sdc = None
        self.flashconfig = None
        self.mtk = mtk
        self.daconfig = daconfig
        self.eh = ErrorHandler()
        self.config = self.mtk.config
        self.usbwrite = self.mtk.port.usbwrite
        self.usbread = self.mtk.port.usbread
        self.echo = self.mtk.port.echo
        self.rbyte = self.mtk.port.rbyte
        self.rdword = self.mtk.port.rdword
        self.rword = self.mtk.port.rword
        self.sectorsize = self.daconfig.pagesize
        self.totalsectors = self.daconfig.flashsize
        self.partition = Partition(self.mtk, self.readflash, self.read_pmt, loglevel)
        self.pathconfig = pathconfig()
        self.patch = False
        self.generatekeys = self.mtk.config.generatekeys
        if self.generatekeys:
            self.patch = True
        self.lft = legacyext(self.mtk, self, loglevel)

    def custom_F0(self, addr: int, dwords: int):
        if self.usbwrite(self.Cmd.GET_FAT_INFO_CMD):  # 0xF0
            self.usbwrite(pack(">I", addr))
            self.usbwrite(pack(">I", dwords))
            res=[unpack(">I", self.usbread(4))[0] for _ in range(dwords)]
            ack = self.usbread(1)
            if ack == self.Rsp.ACK:
                return res

    def read_reg32(self, addr: int):
        if self.usbwrite(self.Cmd.READ_REG32_CMD):  # 0x7A
            self.usbwrite(pack(">I", addr))
            value = unpack(">I", self.usbread(4))[0]
            ack = self.usbread(1)
            if ack == self.Rsp.ACK:
                return value
        return None

    def write_reg32(self, addr: int, data: int):
        self.usbwrite(self.Cmd.WRITE_REG32_CMD)  # 0x7B
        self.usbwrite(pack(">I", addr))
        self.usbwrite(pack(">I", data))
        ack = self.usbread(1)
        if ack == self.Rsp.ACK:
            return True
        return False

    def read_pmt(self):  # A5
        class GptEntries:
            partentries = []

            def __init__(self, sectorsize, totalsectors):
                self.sectorsize = sectorsize
                self.totalsectors = totalsectors

            def print(self):
                print("\nGPT Table:\n-------------")
                for partition in self.partentries:
                    print("{:20} Offset 0x{:016x}, Length 0x{:016x}, Flags 0x{:08x}, UUID {}, Type {}".format(
                        partition.name + ":", partition.sector * self.sectorsize, partition.sectors * self.sectorsize,
                        partition.flags, partition.unique, partition.type))
                print("\nTotal disk size:0x{:016x}, sectors:0x{:016x}".format(self.totalsectors * self.sectorsize,
                                                                              self.totalsectors))

        gpt = GptEntries(self.sectorsize, self.totalsectors)

        class PartitionLegacy:
            type = 0
            unique = b""
            sector = 0
            sectors = 0
            flags = 0
            name = ""

        if self.usbwrite(self.Cmd.SDMMC_READ_PMT_CMD):
            ack = unpack(">B", self.usbread(1))[0]
            if ack == 0x5a:
                datalength = unpack(">I", self.usbread(4))[0]
                if self.usbwrite(self.Rsp.ACK):
                    partdata = self.usbread(datalength)
                    if self.usbwrite(self.Rsp.ACK):
                        if partdata[0x48] == 0xFF:
                            for pos in range(0, datalength, 0x60):
                                partname = partdata[pos:pos + 0x40].rstrip(b"\x00").decode('utf-8')
                                size = unpack("<Q", partdata[pos + 0x40:pos + 0x48])[0]
                                mask_flags = unpack("<Q", partdata[pos + 0x48:pos + 0x50])[0]
                                offset = unpack("<Q", partdata[pos + 0x50:pos + 0x58])[0]
                                p = PartitionLegacy()
                                p.name = partname
                                p.type = 1
                                p.sector = offset // self.daconfig.pagesize
                                p.sectors = size // self.daconfig.pagesize
                                p.flags = mask_flags
                                p.unique = b""
                                gpt.partentries.append(p)
                        else:
                            mask_flags = unpack("<Q", partdata[0x48:0x4C])[0]
                            if 0xA > mask_flags > 0:
                                # 64Bit
                                for pos in range(0, datalength, 0x58):
                                    partname = partdata[pos:pos + 0x40].rstrip(b"\x00").decode('utf-8')
                                    size = unpack("<Q", partdata[pos + 0x40:pos + 0x48])[0]
                                    offset = unpack("<Q", partdata[pos + 0x48:pos + 0x50])[0]
                                    mask_flags = unpack("<Q", partdata[pos + 0x50:pos + 0x58])[0]
                                    p = PartitionLegacy()
                                    p.name = partname
                                    p.type = 1
                                    p.sector = offset // self.daconfig.pagesize
                                    p.sectors = size // self.daconfig.pagesize
                                    p.flags = mask_flags
                                    p.unique = b""
                                    gpt.partentries.append(p)
                            else:
                                # 32Bit
                                for pos in range(0, datalength, 0x4C):
                                    partname = partdata[pos:pos + 0x40]
                                    size = unpack("<Q", partdata[pos + 0x40:pos + 0x44])[0]
                                    offset = unpack("<Q", partdata[pos + 0x44:pos + 0x48])[0]
                                    mask_flags = unpack("<Q", partdata[pos + 0x48:pos + 0x4C])[0]
                                    p = PartitionLegacy()
                                    p.name = partname
                                    p.type = 1
                                    p.sector = offset // self.daconfig.pagesize
                                    p.sectors = size // self.daconfig.pagesize
                                    p.flags = mask_flags
                                    p.unique = b""
                                    gpt.partentries.append(p)
                        return partdata, gpt
        return b"", []

    def get_part_info(self):
        res = self.mtk.port.mtk_cmd(self.Cmd.SDMMC_READ_PMT_CMD, 1 + 4)  # 0xA5
        value, length = unpack(">BI", res)
        self.usbwrite(self.Rsp.ACK)
        data = self.usbread(length)
        self.usbwrite(self.Rsp.ACK)
        return data

    def sdmmc_switch_partition(self, partition):
        if self.usbwrite(self.Cmd.SDMMC_SWITCH_PART_CMD):
            ack = self.usbread(1)
            if ack == self.Rsp.ACK:
                self.usbwrite(pack(">B", partition))
                res = self.usbread(1)
                if res < 0:
                    return False
                else:
                    return True
        return False

    def check_security(self):
        cmd = self.Cmd.CHK_PC_SEC_INFO_CMD + pack(">I", 0)  # E0
        ack = self.mtk.port.mtk_cmd(cmd, 1)
        if ack == self.Rsp.ACK:
            return True
        return False

    def recheck(self):  # If Preloader is needed
        sec_info_len = 0
        cmd = self.Cmd.SECURE_USB_RECHECK_CMD + pack(">I", sec_info_len)  # B4
        status = unpack(">I", self.mtk.port.mtk_cmd(cmd, 1))[0]
        if status == 0x1799:
            return False  # S-USBDL disabled
        return True

    def set_stage2_config(self, hwcode):
        # m_nor_chip_select[0]="CS_0"(0x00), m_nor_chip_select[1]="CS_WITH_DECODER"(0x08)
        self.config.set_da_config(self.daconfig)
        self.usbwrite(pack("B", self.mtk.config.bromver))
        self.usbwrite(pack("B", self.mtk.config.blver))
        m_nor_chip = 0x08
        self.usbwrite(pack(">H", m_nor_chip))
        m_nor_chip_select = 0x00
        self.usbwrite(pack("B", m_nor_chip_select))
        m_nand_acccon = 0x7007FFFF
        self.usbwrite(pack(">I", m_nand_acccon))
        self.config.bmtsettings(self.config.hwcode)
        self.usbwrite(pack("B", self.config.bmtflag))
        self.usbwrite(pack(">I", self.config.bmtpartsize))
        # unsigned char force_charge=0x02; //Setting in tool: 0x02=Auto, 0x01=On
        force_charge = 0x02
        self.usbwrite(pack("B", force_charge))
        resetkeys = 0x01  # default
        if hwcode == 0x6583:
            resetkeys = 0
        self.usbwrite(pack("B", resetkeys))
        # EXT_CLOCK: ext_clock(0x02)="EXT_26M".
        extclock = 0x02
        self.usbwrite(pack("B", extclock))
        msdc_boot_ch = 0
        self.usbwrite(pack("B", msdc_boot_ch))
        toread = 4
        if hwcode == 0x6592:
            is_gpt_solution = 0
            self.usbwrite(pack(">I", is_gpt_solution))
        elif hwcode == 0x6580 or hwcode == 0x8163:
            slc_percent = 0x1
            self.usbwrite(pack(">I", slc_percent))
            unk = b"\x46\x46\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00\x00"
            self.usbwrite(unk)
        elif hwcode in [0x6583, 0x6589]:
            forcedram = 0
            if hwcode == 0x6583:
                forcedram = 0
            elif hwcode == 0x6589:
                forcedram = 1
            self.usbwrite(pack(">I", forcedram))
        elif hwcode == 0x8127:
            skipdl = 0
            self.usbwrite(pack(">I", skipdl))
        elif hwcode == 0x6582:
            newcombo = 1
            self.usbwrite(pack(">I", newcombo))
        time.sleep(0.350)
        buffer = self.usbread(toread)
        if buffer == b'':
            self.error("Didn't receive Stage2 dram info, please check usb cable/hub and retry.")
            return False
        if toread == 4 and buffer == pack(">I", 0xBC3):
            buffer += self.usbread(4)
            pdram = [b"", b""]
            draminfo = self.usbread(16)
            pdram[0] = draminfo[:9]
            draminfo = draminfo[:4][::-1] + draminfo[4:8][::-1] + draminfo[8:12][::-1] + draminfo[12:16][::-1]
            pdram[1] = draminfo[:9]
            self.info("DRAM config needed for : " + hexlify(draminfo).decode('utf-8'))
            if self.daconfig.emi is None:
                found = False
                for root, dirs, files in os.walk(os.path.join(self.pathconfig.get_loader_path(), 'Preloader')):
                    for file in files:
                        with open(os.path.join(root, file), "rb") as rf:
                            data = rf.read()
                            if pdram[0] in data or pdram[1] in data:
                                preloader = os.path.join(root, file)
                                print("Detected preloader: " + preloader)
                                self.daconfig.extract_emi(preloader)
                                found = True
                                break
                    if found:
                        break
            if self.usbread(4) == pack(">I", 0xBC4):  # Nand_Status
                nand_id_count = unpack(">H", self.usbread(2))[0]
                self.info("Reading dram nand info ...")
                nand_ids = []
                for i in range(0, nand_id_count):
                    nand_ids.append(unpack(">H", self.usbread(2))[0])
                if self.daconfig.emi is not None:  # toDo
                    self.usbwrite(self.Cmd.ENABLE_DRAM)  # E8
                    if self.daconfig.emiver == 0:
                        self.usbwrite(pack(">I", 0xFFFFFFFF))
                    else:
                        self.usbwrite(pack(">I", self.daconfig.emiver))
                    ret = self.usbread(1)
                    if ret == self.Rsp.NACK:
                        self.error("EMI Config not accepted :(")
                        return False
                    if ret == self.Rsp.ACK:
                        self.info("Sending dram info ...")
                        dramlength = len(self.daconfig.emi)
                        if self.daconfig.emiver in [0xF, 0x10, 0x14, 0x15]:
                            dramlength = unpack(">I", self.usbread(0x4))[0]  # 0x000000BC
                            self.info("RAM-Length: " + hex(dramlength))
                            self.usbwrite(self.Rsp.ACK)
                            lendram = len(self.daconfig.emi)
                            self.usbwrite(pack(">I", lendram))
                        elif self.daconfig.emiver in [0x0B]:
                            info = self.usbread(0x10)  # 0x000000BC
                            self.info("RAM-Info: " + hexlify(info).decode('utf-8'))
                            dramlength = unpack(">I", self.usbread(0x4))[0]
                            self.usbwrite(self.Rsp.ACK)
                        elif self.daconfig.emiver in [0x0C, 0x0D]:
                            dramlength = unpack(">I", self.usbread(0x4))[0]
                            self.info("RAM-Length: " + hex(dramlength))
                            self.usbwrite(self.Rsp.ACK)
                            self.daconfig.emi = self.daconfig.emi[:dramlength]
                            self.daconfig.emi = pack(">I", 0x100) + self.daconfig.emi[0x4:dramlength]
                        elif self.daconfig.emiver in [0x00]:
                            dramlength = unpack(">I", self.usbread(0x4))[0]  # 0x000000B0
                            self.info("RAM-Length: " + hex(dramlength))
                            self.usbwrite(self.Rsp.ACK)
                            lendram = len(self.daconfig.emi)
                            self.daconfig.emi = self.daconfig.emi[:dramlength]
                            self.usbwrite(pack(">I", dramlength))
                        else:
                            self.warning("Unknown emi version: %d" % self.daconfig.emiver)
                        self.usbwrite(self.daconfig.emi)
                        checksum = unpack(">H", self.usbread(2))[0]  # 0x440C
                        self.info("Checksum: %04X" % checksum)
                        self.usbwrite(self.Rsp.ACK)
                        self.usbwrite(pack(">I", 0x80000001))  # Send DRAM config
                        m_ext_ram_ret = unpack(">I", self.usbread(4))[0]  # 0x00000000 S_DONE
                        self.info(f"M_EXT_RAM_RET : {m_ext_ram_ret}")
                        if m_ext_ram_ret != 0:
                            self.error("Preloader error: 0x%X => %s" % (m_ext_ram_ret, error_to_string(m_ext_ram_ret)))
                            self.mtk.port.close(reset=False)
                            return False
                        m_ext_ram_type = self.usbread(1)[0]  # 0x02 HW_RAM_DRAM
                        self.info(f"M_EXT_RAM_TYPE : {hex(m_ext_ram_type)}")
                        m_ext_ram_chip_select = self.usbread(1)[0]  # 0x00 CS_0
                        self.info(f"M_EXT_RAM_CHIP_SELECT : {hex(m_ext_ram_chip_select)}")
                        m_ext_ram_size = unpack(">Q", self.usbread(8))[0]  # 0x80000000
                        self.info(f"M_EXT_RAM_SIZE : {hex(m_ext_ram_size)}")
                        if self.daconfig.emiver in [0x0D]:
                            self.usbread(4)  # 00000003
                            Raw_0 = self.usbread(4)  # 1C004004
                            Raw_1 = self.usbread(4)  # aa080033
                            CJ_0 = self.usbread(4)  # 00000013
                            CJ_1 = self.usbread(4)  # 00000010
                else:
                    self.error("Preloader needed due to dram config.")
                    self.mtk.port.close(reset=True)
                    return False
        return True

    def read_flash_info_iot(self):
        self.nor = norinfo_iot(self.usbread(0x36))
        self.nand = nandinfo_iot(self.usbread(0x23))
        self.emmc = emmcinfo_iot(self.config,self.usbread(0x2C))
        self.flashconfig = configinfo_iot(self.usbread(0x1E))
        ack=self.usbread(1)
        ack=self.usbread(1)
        m_download_status=int.from_bytes(self.usbread(4),'big')
        m_boot_style = int.from_bytes(self.usbread(4), 'big')
        soc_ok=self.usbread(1)
        if soc_ok==b"\xC1":
            # Security pre-process
            self.usbwrite(b"\x59")
            ack2=self.usbread(1)
            if ack2==b"\xA5":
                # Get Fat Info:
                self.usbwrite(b"\xF0")
                status=self.usbread(4)
                nor_addr=int.from_bytes(self.usbread(4),'big')
                nor_len = int.from_bytes(self.usbread(4), 'big')
                nand_addr = int.from_bytes(self.usbread(4), 'big')
                nand_len = int.from_bytes(self.usbread(4), 'big')
                emmc_addr = int.from_bytes(self.usbread(4), 'big')
                emmc_len = int.from_bytes(self.usbread(4), 'big')
                print(f"Nor addr/len: {hex(nor_addr)}/{hex(nor_len)}")
                print(f"Nand addr/len: {hex(nand_addr)}/{hex(nand_len)}")
                print(f"EMMC addr/len: {hex(emmc_addr)}/{hex(emmc_len)}")
                sys.stdout.flush()
                return True
        return False


    def read_flash_info(self):
        self.nor = norinfo(self.usbread(0x1C))
        data = self.usbread(0x11)
        self.nand = nandinfo64(data)
        nandcount = self.nand.m_nand_flash_id_count
        if nandcount == 0:
            self.nand = nandinfo32(data)
            nandcount = self.nand.m_nand_flash_id_count
            nc = data[-4:] + self.usbread(nandcount * 2 - 4)
        else:
            nc = self.usbread(nandcount * 2)
        m_nand_dev_code = unpack(">" + str(nandcount) + "H", nc)
        self.nand.m_nand_flash_dev_code = m_nand_dev_code
        self.nand.info2 = nandinfo2(self.usbread(9))
        self.emmc = emmcinfo(self.config, self.usbread(0x5C))
        self.sdc = sdcinfo(self.config, self.usbread(0x1C))
        self.flashconfig = configinfo(self.usbread(0x26))
        pi = passinfo(self.usbread(0xA))
        if pi.ack == 0x5A:
            return True
        elif pi.m_download_status == 0x5A:
            tmp = self.usbread(1)
            return True
        return False

    def upload(self):
        if not self.config.iot:
            if self.daconfig.da_loader is None:
                self.error("No valid da loader found... aborting.")
                return False
            loader = self.daconfig.loader
            self.info(f"Uploading legacy stage 1 from {os.path.basename(loader)}")
            with open(loader, 'rb') as bootldr:
                # stage 1
                da1offset = self.daconfig.da_loader.region[1].m_buf
                da1size = self.daconfig.da_loader.region[1].m_len
                da1address = self.daconfig.da_loader.region[1].m_start_addr
                da2address = self.daconfig.da_loader.region[1].m_start_addr
                da1sig_len = self.daconfig.da_loader.region[1].m_sig_len
                bootldr.seek(da1offset)
                da1 = bootldr.read(da1size)
                # ------------------------------------------------
                da2offset = self.daconfig.da_loader.region[2].m_buf
                da2sig_len = self.daconfig.da_loader.region[2].m_sig_len
                bootldr.seek(da2offset)
                da2 = bootldr.read(self.daconfig.da_loader.region[2].m_len)
                if self.mtk.config.is_brom or not self.mtk.config.target_config["sbc"]:
                    hashaddr, hashmode, hashlen = self.mtk.daloader.compute_hash_pos(da1, da2, da2sig_len)
                    if hashaddr is not None:
                        da2patched = self.lft.patch_da2(da2)
                        if da2patched != da2:
                            da1 = self.mtk.daloader.fix_hash(da1, da2patched, hashaddr, hashmode, hashlen)
                            self.patch = True
                            self.daconfig.da2 = da2patched[:hashlen]+da2[hashlen:hashlen+da2sig_len]
                        else:
                            self.daconfig.da2 = da2[:hashlen]+da2[hashlen:hashlen+da2sig_len]
                    else:
                        self.daconfig.da2 = da2[:-da2sig_len]
                else:
                    self.daconfig.da2 = da2[:-da2sig_len]
                if self.mtk.preloader.send_da(da1address, da1size, da1sig_len, da1):
                    if self.mtk.preloader.jump_da(da1address):
                        sync = self.usbread(1)
                        if sync != b"\xC0":
                            self.error("Error on DA sync")
                            return False
                        else:
                            self.info("Got loader sync !")
                    else:
                        return False
                else:
                    return False

            self.info("Reading nand info")
            nandinfo = unpack(">I", self.usbread(4))[0]
            self.debug("NAND_INFO: " + hex(nandinfo))
            ids = unpack(">H", self.usbread(2))[0]
            nandids = []
            for i in range(0, ids):
                tmp = unpack(">H", self.usbread(2))[0]
                nandids.append(tmp)
            self.info("Reading emmc info")
            emmcinfolegacy = unpack(">I", self.usbread(4))[0]
            self.debug("EMMC_INFO: " + hex(emmcinfolegacy))
            emmcids = []
            for i in range(0, 4):
                tmp = unpack(">I", self.usbread(4))[0]
                emmcids.append(tmp)

            if nandids[0] != 0:
                self.daconfig.flashtype = "nand"
            elif emmcids[0] != 0:
                self.daconfig.flashtype = "emmc"
            else:
                self.daconfig.flashtype = "nor"

            self.usbwrite(self.Rsp.ACK)
            ackval = self.usbread(1)
            ackval += self.usbread(1)
            ackval += self.usbread(1)
            self.info("ACK: " + hexlify(ackval).decode('utf-8'))
            self.info("Setting stage 2 config ...")
            if self.set_stage2_config(self.config.hwcode):
                self.info("Uploading stage 2...")
                # stage 2
                if self.brom_send(self.daconfig, self.daconfig.da2, 2):
                    if self.read_flash_info():
                        if self.daconfig.flashtype == "nand":
                            self.daconfig.flashsize = self.nand.m_nand_flash_size
                        elif self.daconfig.flashtype == "emmc" or self.emmc.m_emmc_ua_size!=0:
                            self.daconfig.flashsize = self.emmc.m_emmc_ua_size
                            self.daconfig.flashtype = "emmc"
                            if self.daconfig.flashsize == 0:
                                self.daconfig.flashsize = self.sdc.m_sdmmc_ua_size
                        elif self.daconfig.flashtype == "nor":
                            self.daconfig.flashsize = self.nor.m_nor_flash_size
                        self.info("Connected to preloader")
                        speed = self.check_usb_cmd()
                        if speed[0] == 0:  # 1 = USB High Speed, 2= USB Ultra high speed
                            self.info("Reconnecting to preloader")
                            self.set_usb_cmd()
                            self.mtk.port.close(reset=True)
                            time.sleep(1)
                            while not self.mtk.port.cdc.connect():
                                self.info("Waiting for reconnection")
                                time.sleep(0.5)
                            if self.check_usb_cmd():
                                self.info("Connected to preloader")
                                self.mtk.port.cdc.set_fast_mode(True)
                            else:
                                return False
                        return True
            return False
        else:  # MT6261
            with open(os.path.join("mtkclient","Loader","mt6261_da1.bin"), 'rb') as bootldr:
                da1 = bootldr.read()
                da1size = len(da1)
                da1address = 0x70007000
                da1sig_len = 0x100
            with open(os.path.join("mtkclient","Loader","mt6261_da2.bin"), 'rb') as bootldr:
                da2 = bootldr.read()
                da2size = len(da2)
                da2address = 0x10020000
                da2sig_len = 0x100

            if self.mtk.preloader.send_da(da1address, da1size, da1sig_len, da1):
                if self.mtk.preloader.send_da(da2address, da2size, da2sig_len, da2):
                    if self.mtk.preloader.jump_da(da1address):
                        sync = self.usbread(1)
                        if sync != b"\xC0":
                            self.error("Error on DA sync")
                            return False
                        else:
                            self.info("Got loader sync !")
                    else:
                        return False
                else:
                    return False
            else:
                return False

            da_maj = self.usbread(1)
            da_min = self.usbread(1)
            baseband_chip = self.usbread(1)
            #Disable Download Without Battery
            self.usbwrite(b"\xA5")
            # Brom Version
            self.usbwrite(b"\x05")
            # BLOADER Version
            self.usbwrite(b"\xFE")
            # NOR_CFG: m_nor_chip_select
            self.usbwrite(b"\x00\x08")
            # m_nand_chip_select
            self.usbwrite(b"\x00")
            # m_nand_acccon
            self.usbwrite(b"\x70\x07\xFF\xFF")
            # ext_clock(0x02)="EXT_26M"
            self.usbwrite(b"\x02")

            self.usbwrite(b"\x00\x00\x01\x03")
            ack=self.usbread(1)
            if ack!=b"Z":
                return False
            self.usbwrite(bytes.fromhex("D2 00 00 00 DC 17 04 10 64 01 04 10 00 00 00 00 01 00 BF 00 26 00 01 00 00 00 00 00 68 17 04 10 00 00 00 00"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("D3 00 00 00 1C 18 04 10 64 01 04 10 00 00 00 00 01 00 BF 00 26 00 02 00 00 00 00 00 68 17 04 10 00 00 00 00"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("D4 00 00 00 5C 18 04 10 64 01 04 10 00 00 00 00 01 00 BF 00 26 00 03 00 00 00 00 00 68 17 04 10 00 00 00 00"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("D5 00 00 00 9C 17 04 10 64 01 04 10 00 00 00 00 01 00 BF 00 26 00 28 00 00 00 00 00 68 17 04 10 00 00 00 00"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("D6 00 00 00 DC 17 04 10 64 01 04 10 00 00 00 00 01 00 BF 00 26 00 21 00 00 00 00 00 68 17 04 10 00 00 00 00"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("D7 00 00 00 1C 18 04 10 64 01 04 10 00 00 00 00 01 00 BF 00 26 00 22 00 00 00 00 00 68 17 04 1000 00 00 00"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("D8 00 00 00 5C 18 04 10 64 01 04 10 00 00 00 00 01 00 BF 00 26 00 23 00 00 00 00 00 68 17 04 1000 00 00 00"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("D9 00 00 00 D4 1F 04 10 64 01 04 10 4C 19 04 10 01 00 C2 00 25 00 34 00 00 00 00 00 CC 18 04 10 34 19 04 10"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("10 01 00 00 D4 1F 04 10 64 01 04 10 4C 19 04 10 01 00 C2 00 20 00 14 00 00 00 00 00 CC 18 04 10 34 19 04 10"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("DA 00 00 00 14 20 04 10 64 01 04 10 4C 19 04 10 01 00 C2 00 25 00 35 00 00 00 00 00 CC 18 04 10 34 19 04 10"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("DB 00 00 00 54 20 04 10 64 01 04 10 4C 19 04 10 01 00 C2 00 25 00 36 00 00 00 00 00 CC 18 04 10 34 19 04 10"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("DC 00 00 00 94 20 04 10 64 01 04 10 4C 19 04 10 01 00 C2 00 25 00 37 00 00 00 00 00 CC 18 04 10 34 19 04 10"))
            if self.usbread(1)!=b"i":
                return False
            self.usbwrite(bytes.fromhex("EF 00 00 00 D4 20 04 10 64 01 04 10 4C 19 04 10 01 00 C2 00 25 00 38 00 00 00 00 00 CC 18 04 10 34 19 04 10"))
            v1=self.usbread(1)
            if v1 == b"Z":
                v1 = self.usbread(1)
            self.usbwrite(b"\x00\x00\x00\x00")
            info=int.from_bytes(self.usbread(4),'little')
            if self.read_flash_info_iot():
                if self.nand.m_nand_flash_size != 0:
                    self.daconfig.flashtype = "nand"
                elif self.emmc.m_emmc_ua_size != 0:
                    self.daconfig.flashtype = "emmc"
                else:
                    self.daconfig.flashtype = "nor"

                if self.daconfig.flashtype == "nand":
                    self.daconfig.flashsize = self.nand.m_nand_flash_size
                elif self.daconfig.flashtype == "emmc" or self.emmc.m_emmc_ua_size != 0:
                    self.daconfig.flashsize = self.emmc.m_emmc_ua_size
                    self.daconfig.flashtype = "emmc"
                    if self.daconfig.flashsize == 0:
                        self.daconfig.flashsize = self.sdc.m_sdmmc_ua_size
                elif self.daconfig.flashtype == "nor":
                    self.daconfig.flashsize = self.nor.m_nor_flash_size
                return True

            return False

    def upload_da(self):
        self.info("Uploading legacy da...")
        if self.upload():
            self.info(self.flashconfig)
            if self.daconfig.flashtype == "emmc":
                print(self.emmc)
            elif self.daconfig.flashtype == "nand":
                print(self.nand)
            elif self.daconfig.flashtype == "nor":
                print(self.nor)
            elif self.daconfig.flashtype == "sdc":
                print(self.sdc)
            return True
        return False

    class ShutDownModes:
        NORMAL = 0
        HOME_SCREEN = 1
        FASTBOOT = 2

    def shutdown(self, async_mode: int = 0, dl_bit: int = 0, bootmode: ShutDownModes = ShutDownModes.NORMAL):
        self.finish(bootmode)  # DISCONNECT_USB_AND_RELEASE_POWERKEY
        self.mtk.port.close(reset=True)

    def brom_send(self, dasetup, dadata, stage, packetsize=0x1000):
        offset = dasetup.da_loader.region[stage].m_buf
        dasize=len(dadata)
        size = dasetup.da_loader.region[stage].m_len
        address = dasetup.da_loader.region[stage].m_start_addr
        self.usbwrite(pack(">I", address))
        self.usbwrite(pack(">I", size))
        self.usbwrite(pack(">I", packetsize))
        buffer = self.usbread(1)
        if buffer == self.Rsp.ACK:
            for pos in range(0, size, packetsize):
                self.usbwrite(dadata[pos:pos + packetsize])
                buffer = self.usbread(1)
                if buffer != self.Rsp.ACK:
                    self.error(
                        f"Error on sending brom stage {stage} addr {hex(pos)}: " + hexlify(buffer).decode('utf-8'))
                    self.config.set_gui_status(self.config.tr("Error on sending brom stage"))
                    break
            time.sleep(0.5)
            self.usbwrite(self.Rsp.ACK)
            buffer = self.usbread(1)
            if buffer == self.Rsp.ACK:
                self.info(f"Successfully uploaded stage {stage}")
                self.config.set_gui_status(self.config.tr(f"Successfully uploaded stage {stage}"))
                return True
        else:
            self.error(f"Error on sending brom stage {stage} : " + hexlify(buffer).decode('utf-8'))
            self.config.set_gui_status(self.config.tr("Error on sending brom stage"))
        return False

    def check_usb_cmd(self):
        if self.usbwrite(self.Cmd.USB_CHECK_STATUS):  # 72
            res = self.usbread(1)
            if res == self.Rsp.ACK:
                speed = self.usbread(1)
                return speed
        return None

    def set_usb_cmd(self):
        if self.usbwrite(self.Cmd.USB_SETUP_PORT):  # 72
            if self.usbwrite(b"\x01"):  # USB_HIGH_SPEED
                res = self.usbread(1)
                if len(res) > 0:
                    if res[0] is self.Rsp.ACK[0]:
                        return True
        return False

    def sdmmc_switch_part(self, partition=0x8):
        self.usbwrite(self.Cmd.SDMMC_SWITCH_PART_CMD)  # 60
        ack = self.usbread(1)
        if ack == self.Rsp.ACK:
            # partition = 0x8  # EMMC_Part_User = 0x8, sonst 0x0
            self.usbwrite(pack("B", partition))
            ack = self.usbread(1)
            if ack == self.Rsp.ACK:
                return True
        return False

    def finish(self, value):
        self.usbwrite(self.Cmd.FINISH_CMD)  # D9
        ack = self.usbread(1)[0]
        if ack is self.Rsp.ACK:
            self.usbwrite(pack(">I", value))
            ack = self.usbread(1)[0]
            if ack is self.Rsp.ACK:
                return True
        return False

    def sdmmc_write_data(self, addr, length, filename, offset=0, parttype=None, wdata=None, display=True):
        length, parttype = self.get_parttype(length, parttype)
        storage = self.get_storage()
        fh = False

        if filename is not None:
            fh = open(filename, "rb")
            fh.seek(offset)
        self.mtk.daloader.progress.show_progress("Write", 0, length, display)
        self.usbwrite(self.Cmd.SDMMC_WRITE_DATA_CMD)
        self.usbwrite(pack(">B", storage))
        self.usbwrite(pack(">B", parttype))
        self.usbwrite(pack(">Q", addr))
        self.usbwrite(pack(">Q", length))
        self.usbwrite(pack(">I", 0x100000))
        if self.usbread(1) != self.Rsp.ACK:
            self.error("Couldn't send sdmmc_write_data header")
            return False
        offset = 0
        while offset < length:
            self.usbwrite(self.Rsp.ACK)
            count = min(0x100000, length - offset)
            if fh:
                data = bytearray(fh.read(count))
            else:
                data = wdata[offset:offset + count]
            self.usbwrite(data)
            chksum = sum(data) & 0xFFFF
            self.usbwrite(pack(">H", chksum))
            if self.usbread(1) != self.Rsp.CONT_CHAR:
                self.error("Data ack failed for sdmmc_write_data")
                return False
            self.mtk.daloader.progress.show_progress("Write", offset, length, display)
            offset += count
        if fh:
            fh.close()
        self.mtk.daloader.progress.show_progress("Write", length, length, display)
        return True

    def get_storage(self):
        if self.daconfig.flashtype == "nor":
            storage = DaStorage.MTK_DA_STORAGE_NOR
        elif self.daconfig.flashtype == "nand":
            storage = DaStorage.MTK_DA_STORAGE_NAND
        elif self.daconfig.flashtype == "ufs":
            storage = DaStorage.MTK_DA_STORAGE_UFS
        elif self.daconfig.flashtype == "sdc":
            storage = DaStorage.MTK_DA_STORAGE_SDMMC
        else:
            storage = DaStorage.MTK_DA_STORAGE_EMMC
        return storage

    def sdmmc_write_image(self, addr, length, filename, display=True):
        if filename != "":
            with open(filename, "rb") as rf:
                if self.daconfig.flashtype == "emmc":
                    self.usbwrite(self.Cmd.SDMMC_WRITE_IMAGE_CMD)  # 61
                    self.usbwrite(b"\x00")  # checksum level 0
                    self.usbwrite(b"\x08")  # EMMC_PART_USER
                    self.usbwrite(pack(">Q", addr))
                    self.usbwrite(pack(">Q", length))
                    self.usbwrite(b"\x08")  # index 8
                    self.usbwrite(b"\x03")
                    packetsize = unpack(">I", self.usbread(4))[0]
                    ack = unpack(">B", self.usbread(1))[0]
                    if ack == self.Rsp.ACK[0]:
                        self.usbwrite(self.Rsp.ACK)
                self.mtk.daloader.progress.show_progress("Write", 0, length, display)
                checksum = 0
                bytestowrite = length
                while bytestowrite > 0:
                    size = min(bytestowrite, packetsize)
                    for i in range(0, size, 0x400):
                        data = bytearray(rf.read(size))
                        pos = length - bytestowrite
                        self.mtk.daloader.progress.show_progress("Write", pos, length, display)
                        if self.usbwrite(data):
                            bytestowrite -= size
                            if bytestowrite == 0:
                                checksum = 0
                                for val in data:
                                    checksum += val
                                checksum = checksum & 0xFFFF
                                self.usbwrite(pack(">H", checksum))
                            if self.usbread(1) == b"\x69":
                                if bytestowrite == 0:
                                    self.usbwrite(pack(">H", checksum))
                                if self.usbread(1) == self.Rsp.ACK:
                                    return True
                                else:
                                    self.usbwrite(self.Rsp.ACK)
                self.mtk.daloader.progress.show_progress("Write", length, length, display)
                return True
        return True

    def writeflash(self, addr, length, filename, offset=0, parttype=None, wdata=None, display=True):
        self.mtk.daloader.progress.clear()
        return self.sdmmc_write_data(addr=addr, length=length, filename=filename, offset=offset, parttype=parttype,
                                     wdata=wdata, display=display)

    def formatflash(self, addr, length, parttype=None, display=True):
        self.mtk.daloader.progress.clear()
        length, parttype = self.get_parttype(length, parttype)
        self.check_usb_cmd()
        if self.daconfig.flashtype == "emmc":
            self.sdmmc_switch_part(parttype)
            self.usbwrite(self.Cmd.FORMAT_CMD)  # D6
            self.usbwrite(b"\x02")  # Storage-Type: EMMC
            self.usbwrite(b"\x00")  # 0x00 Nutil erase
            self.usbwrite(b"\x00")  # Validation false
            self.usbwrite(b"\x00")  # NUTL_ADDR_LOGICAL
            self.usbwrite(pack(">Q", addr))
            self.usbwrite(pack(">Q", length))
            progress = 0
            while progress != 100:
                ack = self.usbread(1)[0]
                if ack is not self.Rsp.ACK[0]:
                    self.error(f"Error on sending emmc format command, response: {hex(ack)}")
                    exit(1)
                ack = self.usbread(1)[0]
                if ack is not self.Rsp.ACK[0]:
                    self.error(f"Error on sending emmc format command, response: {hex(ack)}")
                    exit(1)
                data = self.usbread(4)[0]  # PROGRESS_INIT
                progress = self.usbread(1)[0]
                self.usbwrite(b"\x5A")  # Send ACK
                if progress == 0x64:
                    ack = self.usbread(1)[0]
                    if ack is not self.Rsp.ACK[0]:
                        self.error(f"Error on sending emmc format command, response: {hex(ack)}")
                        exit(1)
                    ack = self.usbread(1)[0]
                    if ack is not self.Rsp.ACK[0]:
                        self.error(f"Error on sending emmc format command, response: {hex(ack)}")
                        exit(1)
                    return True
            return False

    def get_parttype(self, length, parttype):
        if self.daconfig.flashtype=="emmc":
            if parttype is None or parttype == "user" or parttype == "":
                length = min(length, self.emmc.m_emmc_ua_size)
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_USER
            elif parttype == "boot1":
                length = min(length, self.emmc.m_emmc_boot1_size)
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_BOOT1
            elif parttype == "boot2":
                length = min(length, self.emmc.m_emmc_boot2_size)
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_BOOT2
            elif parttype == "gp1":
                length = min(length, self.emmc.m_emmc_gp_size[0])
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP1
            elif parttype == "gp2":
                length = min(length, self.emmc.m_emmc_gp_size[1])
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP2
            elif parttype == "gp3":
                length = min(length, self.emmc.m_emmc_gp_size[2])
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP3
            elif parttype == "gp4":
                length = min(length, self.emmc.m_emmc_gp_size[3])
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP4
            elif parttype == "rpmb":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_RPMB
        elif self.daconfig.flashtype == "nand":
            parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_USER
            length = min(length,self.nand.m_nand_flash_size)
        elif self.daconfig.flashtype == "nor":
            parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_USER
            length = min(length, self.nor.m_nor_flash_size)
        else:
            parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_USER
            length = min(length, self.sdc.m_sdmmc_ua_size)
        return length, parttype

    def readflash(self, addr, length, filename, parttype=None, display=True):
        global rq
        self.mtk.daloader.progress.clear()
        length, parttype = self.get_parttype(length, parttype)
        if not self.config.iot:
            self.check_usb_cmd()
        packetsize = 0x0
        if self.daconfig.flashtype == "emmc":
            self.sdmmc_switch_part(parttype)
            packetsize = 0x100000
            self.usbwrite(self.Cmd.READ_CMD)  # D6
            self.usbwrite(b"\x0C")  # Host:Linux, 0x0B=Windows
            self.usbwrite(b"\x02")  # Storage-Type: EMMC
            self.usbwrite(pack(">Q", addr))
            self.usbwrite(pack(">Q", length))
            self.usbwrite(pack(">I", packetsize))
            ack = self.usbread(1)[0]
            if ack is not self.Rsp.ACK[0]:
                self.usbwrite(b"\xA5")
                res = unpack("<I", self.usbread(4))[0]
                self.error(f"Error on sending emmc read command, response: {hex(ack)}, status: {hex(res)}")
                exit(1)
            self.daconfig.readsize = self.daconfig.flashsize
        elif self.daconfig.flashtype == "nand":
            self.usbwrite(self.Cmd.NAND_READPAGE_CMD)  # DF
            self.usbwrite(b"\x0C")  # Host:Linux, 0x0B=Windows
            self.usbwrite(b"\x00")  # Storage-Type: NUTL_READ_PAGE_SPARE
            self.usbwrite(b"\x01")  # Addr-Type: NUTL_ADDR_LOGICAL
            self.usbwrite(pack(">I", addr))
            self.usbwrite(pack(">I", length))
            self.usbwrite(pack(">I", 0))
            ack = self.usbread(1)[0]
            if ack is not self.Rsp.ACK:
                self.error(f"Error on sending nand read command, response: {hex(ack)}")
                exit(1)
            self.daconfig.pagesize = unpack(">I", self.usbread(4))[0]
            self.daconfig.sparesize = unpack(">I", self.usbread(4))[0]
            packetsize = unpack(">I", self.usbread(4))[0]
            pagestoread = 1
            self.usbwrite(pack(">I", pagestoread))
            self.usbread(4)
            self.daconfig.readsize = self.daconfig.flashsize // self.daconfig.pagesize * (
                    self.daconfig.pagesize + self.daconfig.sparesize)
        elif self.daconfig.flashtype == "nor":
                packetsize = 0x400
                self.usbwrite(self.Cmd.READ_CMD)  # D6
                if not self.config.iot:
                    self.usbwrite(b"\x0C")  # Host:Linux, 0x0B=Windows
                self.usbwrite(b"\x00")  # Storage-Type: EMMC
                if self.config.iot:
                    self.usbwrite(pack(">I", addr))
                    self.usbwrite(pack(">I", length))
                    self.usbwrite(pack(">I", packetsize))
                else:
                    self.usbwrite(pack(">Q", addr))
                    self.usbwrite(pack(">Q", length))
                    self.usbwrite(pack(">I", packetsize))
                ack = self.usbread(1)[0]
                if ack is not self.Rsp.ACK[0]:
                    self.usbwrite(b"\xA5")
                    res = unpack("<I", self.usbread(4))[0]
                    self.error(f"Error on sending emmc read command, response: {hex(ack)}, status: {hex(res)}")
                    exit(1)
                self.daconfig.readsize = self.daconfig.flashsize
        if display:
            self.mtk.daloader.progress.show_progress("Read", 0, length, display)
        if filename != "":
            worker = Thread(target=writedata, args=(filename, rq), daemon=True)
            worker.start()
            bytestoread = length
            while bytestoread > 0:
                size = bytestoread
                if bytestoread > packetsize:
                    size = packetsize
                rq.put(self.usbread(size))
                bytestoread -= size
                checksum = unpack(">H", self.usbread(1) + self.usbread(1))[0]
                self.debug("Checksum: %04X" % checksum)
                self.usbwrite(self.Rsp.ACK)
                if length > bytestoread:
                    rpos = length - bytestoread
                else:
                    rpos = 0
                self.mtk.daloader.progress.show_progress("Read", rpos, length, display)
            self.mtk.daloader.progress.show_progress("Read", length, length, display)
            rq.put(None)
            worker.join(60)
            return True
        else:
            buffer = bytearray()
            bytestoread = length
            self.mtk.daloader.progress.show_progress("Read", 0, length, display)
            while bytestoread > 0:
                size = bytestoread
                if bytestoread > packetsize:
                    size = packetsize
                buffer.extend(self.usbread(size))
                bytestoread -= size
                checksum = unpack(">H", self.usbread(2))[0]
                self.debug("Checksum: %04X" % checksum)
                self.usbwrite(self.Rsp.ACK)
                if length > bytestoread:
                    rpos = length - bytestoread
                else:
                    rpos = 0
                self.mtk.daloader.progress.show_progress("Read", rpos, length, display)
            self.mtk.daloader.progress.show_progress("Read", length, length, display)
            return buffer
