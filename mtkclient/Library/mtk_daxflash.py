#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 MIT License
import logging
import time
import os
import hashlib
from binascii import hexlify
from struct import pack, unpack
from mtkclient.Library.utils import LogBase, progress, logsetup
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.daconfig import EMMC_PartitionType, UFS_PartitionType, DaStorage
from mtkclient.Library.partition import Partition
from mtkclient.Library.rw_patch import write32, read32
from mtkclient.Library.hwcrypto import crypto_setup, hwcrypto
from mtkclient.config.payloads import pathconfig

def find_binary(data, strf, pos=0):
    t = strf.split(b".")
    pre = 0
    offsets = []
    while pre != -1:
        pre = data[pos:].find(t[0], pre)
        if pre == -1:
            if len(offsets) > 0:
                for offset in offsets:
                    error = 0
                    rt = offset + len(t[0])
                    for i in range(1, len(t)):
                        if t[i] == b'':
                            rt += 1
                            continue
                        rt += 1
                        prep = data[rt:].find(t[i])
                        if prep != 0:
                            error = 1
                            break
                        rt += len(t[i])
                    if error == 0:
                        return pos + offset
            else:
                return -1
        else:
            offsets.append(pre)
            pre += 1
    return -1


class NandExtension:
    # uni=0, multi=1
    cellusage = 0
    # logical=0, physical=1, physical_pmt=2
    addr_type = 0
    # raw=0, ubi_img=1, ftl_img=2
    bin_type = 0
    # operation_type -> spare=0,page=1,page_ecc=2,page_spare_ecc=3,verify=4,page_spare_norandom,page_fdm
    # nand_format_level -> format_normal=0,force=1,mark_bad_block=2,level_end=3
    operation_type = 0  # or nand_format_level
    sys_slc_percent = 0
    usr_slc_percent = 0
    phy_max_size = 0


def addr_to_block(addr, blocksize):
    return addr // blocksize


class DAXFlash(metaclass=LogBase):
    class Cmd:
        MAGIC = 0xFEEEEEEF
        SYNC_SIGNAL = 0x434E5953

        UNKNOWN = 0x010000
        DOWNLOAD = 0x010001
        UPLOAD = 0x010002
        FORMAT = 0x010003
        WRITE_DATA = 0x010004
        READ_DATA = 0x010005
        FORMAT_PARTITION = 0x010006
        SHUTDOWN = 0x010007
        BOOT_TO = 0x010008
        DEVICE_CTRL = 0x010009
        INIT_EXT_RAM = 0x01000A
        SWITCH_USB_SPEED = 0x01000B
        READ_OTP_ZONE = 0x01000C
        WRITE_OTP_ZONE = 0x01000D
        WRITE_EFUSE = 0x01000E
        READ_EFUSE = 0x01000F
        NAND_BMT_REMARK = 0x010010
        SETUP_ENVIRONMENT = 0x010100
        SETUP_HW_INIT_PARAMS = 0x010101

        SET_BMT_PERCENTAGE = 0x020001
        SET_BATTERY_OPT = 0x020002
        SET_CHECKSUM_LEVEL = 0x020003
        SET_RESET_KEY = 0x020004
        SET_HOST_INFO = 0x020005
        SET_META_BOOT_MODE = 0x020006
        SET_EMMC_HWRESET_PIN = 0x020007
        SET_GENERATE_GPX = 0x020008
        SET_REGISTER_VALUE = 0x020009
        SET_EXTERNAL_SIG = 0x02000A
        SET_REMOTE_SEC_POLICY = 0x02000B
        SET_ALL_IN_ONE_SIG = 0x02000C
        SET_RSC_INFO = 0x02000D
        SET_UPDATE_FW = 0x020010
        SET_UFS_CONFIG = 0x020011

        GET_EMMC_INFO = 0x040001
        GET_NAND_INFO = 0x040002
        GET_NOR_INFO = 0x040003
        GET_UFS_INFO = 0x040004
        GET_VERSION = 0x040005
        GET_EXPIRE_DATA = 0x040006
        GET_PACKET_LENGTH = 0x040007
        GET_RANDOM_ID = 0x040008
        GET_PARTITION_TBL_CATA = 0x040009
        GET_CONNECTION_AGENT = 0x04000A
        GET_USB_SPEED = 0x04000B
        GET_RAM_INFO = 0x04000C
        GET_CHIP_ID = 0x04000D
        GET_OTP_LOCK_STATUS = 0x04000E
        GET_BATTERY_VOLTAGE = 0x04000F
        GET_RPMB_STATUS = 0x040010
        GET_EXPIRE_DATE = 0x040011
        GET_DRAM_TYPE = 0x040012
        GET_DEV_FW_INFO = 0x040013
        GET_HRID = 0x040014
        GET_ERROR_DETAIL = 0x040015

        START_DL_INFO = 0x080001
        END_DL_INFO = 0x080002
        ACT_LOCK_OTP_ZONE = 0x080003
        DISABLE_EMMC_HWRESET_PIN = 0x080004
        CC_OPTIONAL_DOWNLOAD_ACT = 0x800005
        DA_STOR_LIFE_CYCLE_CHECK = 0x080007

        UNKNOWN_CTRL_CODE = 0x0E0000
        CTRL_STORAGE_TEST = 0x0E0001
        CTRL_RAM_TEST = 0x0E0002
        DEVICE_CTRL_READ_REGISTER = 0x0E0003

    class ChecksumAlgorithm:
        PLAIN = 0
        CRC32 = 1
        MD5 = 2

    class FtSystemOSE:
        OS_WIN = 0
        OS_LINUX = 1

    class DataType:
        DT_PROTOCOL_FLOW = 1
        DT_MESSAGE = 2

    def __init__(self, mtk, daconfig, loglevel=logging.INFO):
        self.__logger = logsetup(self, self.__logger, loglevel)
        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.error = self.__logger.error
        self.warning = self.__logger.warning
        self.mtk = mtk
        self.loglevel = loglevel
        self.sram = None
        self.dram = None
        self.emmc = None
        self.nand = None
        self.nor = None
        self.ufs = None
        self.chipid = None
        self.randomid = None
        self.__logger = self.__logger
        self.eh = ErrorHandler()
        self.config = self.mtk.config
        self.usbwrite = self.mtk.port.usbwrite
        self.usbread = self.mtk.port.usbread
        self.echo = self.mtk.port.echo
        self.rbyte = self.mtk.port.rbyte
        self.rdword = self.mtk.port.rdword
        self.rword = self.mtk.port.rword
        self.daconfig = daconfig
        self.partition = Partition(self.mtk, self.readflash, self.read_pmt, loglevel)
        self.progress = progress(self.daconfig.pagesize)
        self.pathconfig = pathconfig()

    def ack(self, rstatus=True):
        try:
            tmp = pack("<III", self.Cmd.MAGIC, self.DataType.DT_PROTOCOL_FLOW, 4)
            self.usbwrite(tmp)
            data = pack("<I", 0)
            self.usbwrite(data)
            # time.sleep(0.0001)
            if rstatus:
                status = self.status()
                return status
            return True
        except:
            return -1

    def send(self, data, datatype=DataType.DT_PROTOCOL_FLOW):
        if isinstance(data, int):
            data = pack("<I", data)
            length = 4
        else:
            length = len(data)
        tmp = pack("<III", self.Cmd.MAGIC, datatype, length)
        if self.usbwrite(tmp):
            return self.usbwrite(data)
        return False

    def recv(self):
        magic, datatype, length = unpack("<III", self.usbread(4 + 4 + 4))
        resp = self.usbread(length)
        return resp

    def rdword(self, count=1):
        data = []
        for i in range(count):
            data.append(unpack("<I", self.recv())[0])
        if count == 1:
            return data[0]
        return data

    def status(self):
        status = None
        bytestoread = 4 + 4 + 4
        hdr = self.usbread(bytestoread)
        magic, datatype, length = unpack("<III", hdr)
        if magic != 0xFEEEEEEF:
            self.error("Status error")
            return -1
        tmp = self.usbread(length)
        try:
            status = unpack("<" + str(length // 4) + "I", tmp)[0]
            if status == 0xFEEEEEEF:
                return 0
        except:
            status = status
            pass
        return status

    def read_pmt(self):
        return b"", []

    def send_param(self, params):
        if isinstance(params, bytes):
            params = [params]
        for param in params:
            pkt = pack("<III", self.Cmd.MAGIC, self.DataType.DT_PROTOCOL_FLOW, len(param))
            if self.usbwrite(pkt):
                # time.sleep(0.05)
                length = len(param)
                pos = 0
                while length > 0:
                    dsize = min(length, 0x200)
                    if not self.usbwrite(param[pos:pos + dsize]):
                        break
                    pos += dsize
                    length -= dsize
        status = self.status()
        if status == 0:
            return True
        else:
            if status!=0xc0040050:
                self.error(f"Error on sending parameter: {self.eh.status(status)}")
        return False


    def send_devctrl(self, cmd, param=None, status=None):
        if status is None:
            status = [0]
        if self.send(self.Cmd.DEVICE_CTRL):
            status[0] = self.status()
            if status[0] == 0x0:
                if self.send(cmd):
                    status[0] = self.status()
                    if status[0] == 0x0:
                        if param is None:
                            return self.recv()
                        else:
                            return self.send_param(param)
        if status[0] != 0xC0010004:
            self.error(f"Error on sending dev ctrl {cmd}:"+self.eh.status(status[0]))
        return b""

    def set_reset_key(self, reset_key=0x68):
        # default:0x0,one:0x50,two:0x68
        param = pack("<I", reset_key)
        return self.send_devctrl(self.Cmd.SET_RESET_KEY, param)

    def set_checksum_level(self, checksum_level=0x0):
        param = pack("<I", checksum_level)
        # none[0x0]. USB[0x1]. storage[0x2], both[0x3]
        return self.send_devctrl(self.Cmd.SET_CHECKSUM_LEVEL, param)

    def set_battery_opt(self, option=0x2):
        param = pack("<I", option)
        # battery[0x0]. USB power[0x1]. auto[0x2]
        return self.send_devctrl(self.Cmd.SET_BATTERY_OPT, param)

    def send_emi(self, emi):
        if self.send(self.Cmd.INIT_EXT_RAM):
            status=self.status()
            if status==0:
                if self.send(pack("<I", len(emi))):
                    return self.send_param([emi])
            else:
                self.error(f"Error on sending emi: {self.eh.status(status)}")
        return False

    def send_data(self, data):
        pkt2 = pack("<III", self.Cmd.MAGIC, self.DataType.DT_PROTOCOL_FLOW, len(data))
        if self.usbwrite(pkt2):
            bytestowrite = len(data)
            pos = 0
            while bytestowrite > 0:
                if self.usbwrite(data[pos:pos + 64]):
                    pos += 64
                    bytestowrite -= 64
            status = self.status()
            if status == 0x0:
                return True
            else:
                self.error(f"Error on sending data: {self.eh.status(status)}")
                return False

    def compute_hash_pos(self, da2, bootldr):
        da1offset = self.daconfig.da[2]["m_buf"]
        da1size = self.daconfig.da[2]["m_len"] - self.daconfig.da[1]["m_sig_len"]
        da1address = self.daconfig.da[2]["m_start_addr"]  # at_address
        da2offset = self.daconfig.da[3]["m_buf"]
        da2size = self.daconfig.da[3]["m_len"] - self.daconfig.da[3]["m_sig_len"]
        hashdigest = hashlib.sha1(da2).digest()
        hashdigest256 = hashlib.sha256(da2).digest()
        bootldr.seek(da1offset)
        da1 = bootldr.read(da1size)
        idx = da1.find(hashdigest)
        hashmode = 1
        if idx == -1:
            idx = da1.find(hashdigest256)
            hashmode = 2
        if idx != -1:
            return da1address + idx, hashmode
        return None, None

    def read(self, addr, dwords=1):
        res = []
        for pos in range(dwords):
            if self.send(self.Cmd.DOWNLOAD):
                status=self.status()
                if status==0x0:
                    param = pack("<I", addr + (pos * 4))
                    pkt1 = pack("<III", self.Cmd.MAGIC, self.DataType.DT_PROTOCOL_FLOW, len(param))
                    if self.usbwrite(pkt1):
                        if self.usbwrite(param):
                            val = self.status()
                            if dwords == 1:
                                return val
                            res.append(val)
                else:
                    self.error(f"Error on download: {self.eh.status(status)}")
        return res

    def write(self, addr, dwords):
        if isinstance(dwords, int):
            dwords = [dwords]
        pos = 0
        for val in dwords:
            if self.send(self.Cmd.UPLOAD):
                status=self.status()
                if status==0x0:
                    param = pack("<II", addr + pos, val)
                    pkt1 = pack("<III", self.Cmd.MAGIC, self.DataType.DT_PROTOCOL_FLOW, len(param))
                    if self.usbwrite(pkt1):
                        if self.usbwrite(param):
                            self.status()
                            if len(dwords) == 1:
                                return True
                else:
                    self.error(f"Error on upload: {self.eh.status(status)}")
                    return False
            pos += 4
        return True

    def writemem(self, addr, data):
        for i in range(0, len(data), 4):
            value = data[i:i + 4]
            while len(value) < 4:
                value += b"\x00"
            self.write(addr + i, unpack("<I", value))
        return True

    def boot_to(self, at_address, da, display=True):  # =0x40000000
        if self.send(self.Cmd.BOOT_TO):
            if self.status() == 0:
                param = pack("<QQ", at_address, len(da))
                pkt1 = pack("<III", self.Cmd.MAGIC, self.DataType.DT_PROTOCOL_FLOW, len(param))
                if self.usbwrite(pkt1):
                    if self.usbwrite(param):
                        if self.send_data(da):
                            time.sleep(0.5)
                            status = self.status()
                            if status == 0x434E5953 or status == 0x0:
                                return True
                            else:
                                self.error(f"Error on boot to: {self.eh.status(status)}")
        return False

    def get_connection_agent(self):
        # brom
        res = self.send_devctrl(self.Cmd.GET_CONNECTION_AGENT)
        status = self.status()
        if status == 0x0:
            return res
        else:
            self.error(f"Error on getting connection agent: {self.eh.status(status)}")
        return None

    """
    def get_dram_type(self):
        res = self.send_devctrl(self.Cmd.GET_DRAM_TYPE)
        status = self.status()
        if status == 0x0:
            return res
    """

    def partitiontype_and_size(self, storage, parttype, length):
        if storage == DaStorage.MTK_DA_STORAGE_EMMC or storage == DaStorage.MTK_DA_STORAGE_SDMMC:
            storage = 1
            if parttype is None or parttype == "user":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_USER
            elif parttype == "boot1":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_BOOT1
                if self.daconfig.flashtype == "emmc":
                    length = min(length, self.emmc.boot1_size)
            elif parttype == "boot2":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_BOOT2
                if self.daconfig.flashtype == "emmc":
                    length = min(length, self.emmc.boot2_size)
            elif parttype == "gp1":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP1
                if self.daconfig.flashtype == "emmc":
                    length = min(length, self.emmc.gp1_size)
            elif parttype == "gp2":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP2
                if self.daconfig.flashtype == "emmc":
                    length = min(length, self.emmc.gp2_size)
            elif parttype == "gp3":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP3
                if self.daconfig.flashtype == "emmc":
                    length = min(length, self.emmc.gp3_size)
            elif parttype == "gp4":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_GP4
                if self.daconfig.flashtype == "emmc":
                    length = min(length, self.emmc.gp4_size)
            elif parttype == "rpmb":
                parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_RPMB
                if self.daconfig.flashtype == "emmc":
                    length = min(length, self.emmc.rpmb_size)
            else:
                self.error("Unknown parttype. Known parttypes are \"boot1\",\"boot2\",\"gp1\"," +
                           "\"gp2\",\"gp3\",\"gp4\",\"rpmb\"")
                return []
        elif storage == DaStorage.MTK_DA_STORAGE_UFS:
            if parttype is None or parttype == "lu3":  # USER
                parttype = UFS_PartitionType.UFS_LU3
                length = min(length, self.ufs.lu0_size)
            elif parttype == "lu1":  # BOOT1
                parttype = UFS_PartitionType.UFS_LU1
                length = min(length, self.ufs.lu1_size)
            elif parttype == "lu2":  # BOOT2
                parttype = UFS_PartitionType.UFS_LU2
                length = min(length, self.ufs.lu2_size)
            elif parttype == "lu4":  # RPMB
                parttype = UFS_PartitionType.UFS_LU4
                length = min(length, self.ufs.lu2_size)
            else:
                self.error("Unknown parttype. Known parttypes are \"lu1\",\"lu2\"," +
                           "\"lu3\"", "\"lu4\"")
                return []
        elif storage in [DaStorage.MTK_DA_STORAGE_NAND, DaStorage.MTK_DA_STORAGE_NAND_MLC,
                         DaStorage.MTK_DA_STORAGE_NAND_SLC, DaStorage.MTK_DA_STORAGE_NAND_TLC,
                         DaStorage.MTK_DA_STORAGE_NAND_SPI, DaStorage.MTK_DA_STORAGE_NAND_AMLC]:
            parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_USER
            length = min(length, self.nand.total_size)
        elif storage in [DaStorage.MTK_DA_STORAGE_NOR, DaStorage.MTK_DA_STORAGE_NOR_PARALLEL,
                         DaStorage.MTK_DA_STORAGE_NOR_SERIAL]:
            parttype = EMMC_PartitionType.MTK_DA_EMMC_PART_USER
            length = min(length, self.nor.available_size)
        return [storage, parttype, length]

    def formatflash(self, addr, length, storage=DaStorage.MTK_DA_STORAGE_EMMC,
                    parttype=EMMC_PartitionType.MTK_DA_EMMC_PART_USER, display=False):
        part_info = self.partitiontype_and_size(storage, parttype, length)
        if not part_info:
            return False
        storage, parttype, length = part_info

        if self.send(self.Cmd.FORMAT):
            status=self.status()
            if status == 0:
                # storage: emmc:1,slc,nand,nor,ufs
                # section: boot,user of emmc:8, LU1, LU2

                ne = NandExtension()
                param = pack("<IIQQ", storage, parttype, addr, length)
                param += pack("<IIIIIIII", ne.cellusage, ne.addr_type, ne.bin_type, ne.operation_type,
                              ne.sys_slc_percent, ne.usr_slc_percent, ne.phy_max_size, 0x0)
                self.send_param(param)
                status = self.status()
                while status == 0x40040004:  # STATUS_CONTINUE
                    # it receive some data maybe sleep in ms time,
                    time.sleep(self.status() / 1000.0)
                    status = self.ack()
                if status == 0x40040005:  # STATUS_COMPLETE
                    return True

            if status!=0x0:
                self.error(f"Error on format: {self.eh.status(status)}")
        return False

    def get_chip_id(self):
        class Chipid:
            hw_code = 0
            hw_sub_code = 0
            hw_version = 0
            sw_version = 0
            chip_evolution = 0

        cid = Chipid
        data = self.send_devctrl(self.Cmd.GET_CHIP_ID)
        cid.hw_code, cid.hw_sub_code, cid.hw_version, cid.sw_version, cid.chip_evolution = unpack(">HHHHH",
                                                                                                  data[:(5 * 2)])
        status=self.status()
        if status == 0:
            return cid
        else:
            self.error(f"Error on getting chip id: {self.eh.status(status)}")
        return None

    def get_ram_info(self):
        resp = self.send_devctrl(self.Cmd.GET_RAM_INFO)
        status=self.status()
        if status == 0x0:
            class RamInfo:
                type = 0
                base_address = 0
                size = 0

            sram = RamInfo()
            dram = RamInfo()
            if len(resp) == 24:
                sram.type, sram.base_address, sram.size, dram.type, dram.base_address, dram.size = unpack("<IIIIII",
                                                                                                          resp)
            elif len(resp) == 48:
                sram.type, sram.base_address, sram.size, dram.type, dram.base_address, dram.size = unpack("<QQQQQQ",
                                                                                                          resp)

            return sram, dram
        else:
            self.error(f"Error on getting ram info: {self.eh.status(status)}")
        return None, None

    def get_emmc_info(self, display=True):
        resp = self.send_devctrl(self.Cmd.GET_EMMC_INFO)
        if resp == b'':
            return None
        status=self.status()
        if status == 0:
            class EmmcInfo:
                type = 1  # emmc or sdmmc or none
                block_size = 0x200
                boot1_size = 0
                boot2_size = 0
                rpmb_size = 0
                gp1_size = 0
                gp2_size = 0
                gp3_size = 0
                gp4_size = 0
                user_size = 0
                cid = b""
                fwver = 0
                unknown = b""

            emmc = EmmcInfo()
            pos = 0
            emmc.type, emmc.block_size = unpack("<II", resp[pos:pos + 8])
            pos += 8
            emmc.boot1_size, emmc.boot2_size, emmc.rpmb_size, emmc.gp1_size, emmc.gp2_size, emmc.gp3_size, \
            emmc.gp4_size, emmc.user_size = unpack("<QQQQQQQQ", resp[pos:pos + (8 * 8)])
            pos += 8 * 8
            emmc.cid = resp[pos:pos + (4 * 4)]
            pos += (4 * 4)
            emmc.fwver = unpack("<Q", resp[pos:pos + 8])[0]
            pos += 8
            emmc.unknown = resp[pos:]
            if emmc.type != 0 and display:
                self.info(f"EMMC FWVer:      {hex(emmc.fwver)}")
                self.info(f"EMMC CID:        {hexlify(emmc.cid).decode('utf-8')}")
                self.info(f"EMMC Boot1 Size: {hex(emmc.boot1_size)}")
                self.info(f"EMMC Boot2 Size: {hex(emmc.boot2_size)}")
                self.info(f"EMMC GP1 Size:   {hex(emmc.gp1_size)}")
                self.info(f"EMMC GP2 Size:   {hex(emmc.gp2_size)}")
                self.info(f"EMMC GP3 Size:   {hex(emmc.gp3_size)}")
                self.info(f"EMMC GP4 Size:   {hex(emmc.gp4_size)}")
                self.info(f"EMMC RPMB Size:  {hex(emmc.rpmb_size)}")
                self.info(f"EMMC USER Size:  {hex(emmc.user_size)}")
            return emmc
        else:
            self.error(f"Error on getting emmc info: {self.eh.status(status)}")
        return None

    def get_nand_info(self):
        resp = self.send_devctrl(self.Cmd.GET_NAND_INFO)
        status=self.status()
        if status == 0:
            class NandInfo:
                type = 1  # slc, mlc, spi, none
                page_size = 0
                block_size = 0x200
                spare_size = 0
                total_size = 0
                available_size = 0
                nand_bmt_exist = 0
                nand_id = 0

            nand = NandInfo()
            pos = 0
            nand.type, nand.page_size, nand.block_size, nand.spare_size = unpack("<IIII", resp[pos:pos + 16])
            pos += 16
            nand.total_size, nand.available_size = unpack("<QQ", resp[pos:pos + (2 * 8)])
            pos += 2 * 8
            nand.nand_bmt_exist = resp[pos:pos + 1]
            pos += 1
            nand.nand_id = unpack("<12B", resp[pos:pos + 12])
            if nand.type != 0:
                self.info(f"NAND Pagesize:   {hex(nand.page_size)}")
                self.info(f"NAND Blocksize:  {hex(nand.block_size)}")
                self.info(f"NAND Sparesize:  {hex(nand.spare_size)}")
                self.info(f"NAND Total size: {hex(nand.total_size)}")
                self.info(f"NAND Avail:      {hex(nand.available_size)}")
                self.info(f"NAND ID:         {hexlify(nand.nand_id).decode('utf-8')}")
            return nand
        else:
            self.error(f"Error on getting nand info: {self.eh.status(status)}")
        return None

    def get_nor_info(self):
        resp = self.send_devctrl(self.Cmd.GET_NOR_INFO)
        status=self.status()
        if status == 0:
            class NorInfo:
                type = 1  # nor, none
                page_size = 0
                available_size = 0

            nor = NorInfo()
            nor.type, nor.page_size, nor.available_size = unpack("<IIQ", resp[:16])
            if nor.type != 0:
                self.info(f"NOR Pagesize: {hex(nor.page_size)}")
                self.info(f"NOR Size:     {hex(nor.available_size)}")
            return nor
        else:
            self.error(f"Error on getting nor info: {self.eh.status(status)}")
        return None

    def get_ufs_info(self):
        resp = self.send_devctrl(self.Cmd.GET_UFS_INFO)
        status=self.status()
        if status == 0:
            class UfsInfo:
                type = 1  # nor, none
                block_size = 0
                lu0_size = 0
                lu1_size = 0
                lu2_size = 0
                cid = b""
                fwver = 0

            ufs = UfsInfo()
            ufs.type, ufs.block_size, ufs.lu2_size, ufs.lu1_size, ufs.lu0_size = unpack("<IIQQQ",
                                                                                        resp[:(2 * 4) + (3 * 8)])
            pos = (2 * 4) + (3 * 8)
            ufs.cid = resp[pos:pos + 16]
            ufs.fwver = unpack("<I", resp[pos + 16:pos + 16 + 4])[0]
            if ufs.type != 0:
                self.info(f"UFS FWVer:    {hex(ufs.fwver)}")
                self.info(f"UFS Blocksize:{hex(ufs.block_size)}")
                self.info(f"UFS CID:      {hexlify(ufs.cid).decode('utf-8')}")
                self.info(f"UFS LU0 Size: {hex(ufs.lu0_size)}")
                self.info(f"UFS LU1 Size: {hex(ufs.lu1_size)}")
                self.info(f"UFS LU2 Size: {hex(ufs.lu2_size)}")
                self.mtk.config.pagesize = ufs.block_size
                self.mtk.daloader.daconfig.pagesize = ufs.block_size
            return ufs
        else:
            self.error(f"Error on getting ufs info: {self.eh.status(status)}")
        return None

    def get_expire_date(self):
        res = self.send_devctrl(self.Cmd.GET_EXPIRE_DATE)
        if res != b"":
            status=self.status()
            if status == 0x0:
                return res
            else:
                self.error(f"Error on getting expire date: {self.eh.status(status)}")
        return None

    def get_random_id(self):
        res = self.send_devctrl(self.Cmd.GET_RANDOM_ID)
        status=self.status()
        if status == 0:
            return res
        else:
            self.error(f"Error on getting random id: {self.eh.status(status)}")
        return None

    def get_hrid(self):
        res = self.send_devctrl(self.Cmd.GET_HRID)
        status=self.status()
        if status == 0:
            return res
        else:
            self.error(f"Error on getting hrid info: {self.eh.status(status)}")
        return None

    def get_dev_fw_info(self):
        res = self.send_devctrl(self.Cmd.GET_DEV_FW_INFO)
        status=self.status()
        if status == 0:
            return res
        else:
            self.error(f"Error on getting dev fw info: {self.eh.status(status)}")
        return None

    def get_da_stor_life_check(self):
        res = self.send_devctrl(self.Cmd.DA_STOR_LIFE_CYCLE_CHECK)
        return unpack("<I", res)[0]

    def get_packet_length(self):
        resp = self.send_devctrl(self.Cmd.GET_PACKET_LENGTH)
        status = self.status()
        if status == 0:
            class Packetlen:
                write_packet_length = 0
                read_packet_length = 0

            plen = Packetlen()
            plen.write_packet_length, plen.read_packet_length = unpack("<II", resp)
            return plen
        else:
            self.error(f"Error on getting packet length: {self.eh.status(status)}")
        return None

    def cmd_write_data(self, addr, size, storage=DaStorage.MTK_DA_STORAGE_EMMC,
                       parttype=EMMC_PartitionType.MTK_DA_EMMC_PART_USER):
        if self.send(self.Cmd.WRITE_DATA):
            status=self.status()
            if status == 0:
                # storage: emmc:1,slc,nand,nor,ufs
                # section: boot,user of emmc:8, LU1, LU2
                ne = NandExtension()
                param = pack("<IIQQ", storage, parttype, addr, size)
                param += pack("<IIIIIIII", ne.cellusage, ne.addr_type, ne.bin_type, ne.operation_type,
                              ne.sys_slc_percent, ne.usr_slc_percent, ne.phy_max_size, 0x0)
                if self.send_param(param):
                    return True
            else:
                self.error(f"Error on writing data: {self.eh.status(status)}")
        return False

    def cmd_read_data(self, addr, size, storage=DaStorage.MTK_DA_STORAGE_EMMC,
                      parttype=EMMC_PartitionType.MTK_DA_EMMC_PART_USER):
        if self.send(self.Cmd.READ_DATA):
            status=self.status()
            if status == 0:
                # storage: emmc:1,slc,nand,nor,ufs
                # section: boot,user of emmc:8, LU1, LU2
                ne = NandExtension()
                param = pack("<IIQQ", storage, parttype, addr, size)
                param += pack("<IIIIIIII", ne.cellusage, ne.addr_type, ne.bin_type, ne.operation_type,
                              ne.sys_slc_percent, ne.usr_slc_percent, ne.phy_max_size, 0x0)
                self.send_param(param)
                status = self.status()
                if status == 0x0:
                    return True
            if status != 0x0:
                self.error(f"Error on reading data: {self.eh.status(status)}")
        return False

    def readflash(self, addr, length, filename, parttype=None, display=True):
        partinfo = self.getstorage(parttype, length)
        if not partinfo:
            return False
        storage, parttype, length = partinfo
        if self.cmd_read_data(addr=addr, size=length, storage=storage, parttype=parttype):
            bytestoread = length
            if filename != "":
                try:
                    with open(filename, "wb") as wf:
                        while bytestoread > 0:
                            magic, datatype, slength = unpack("<III", self.usbread(4 + 4 + 4))
                            if magic == 0xFEEEEEEF:
                                tmp = self.usbread(slength)
                                wf.write(tmp)
                                bytestoread -= len(tmp)
                                if self.ack() != 0:
                                    return False
                                if display:
                                    self.progress.show_progress("Read", length - bytestoread, length, display)
                            else:
                                return False

                except Exception as err:
                    self.error("Couldn't write to " + filename + ". Error: " + str(err))
                    return False
                return True
            else:
                buffer = bytearray()
                while length > 0:
                    tmp = self.recv()
                    buffer.extend(tmp)
                    if self.ack() != 0:
                        break
                    if display:
                        self.progress.show_progress("Read", length - bytestoread, length, display)
                    length -= len(tmp)
                return buffer
        return False

    def close(self):
        if self.send(self.Cmd.SHUTDOWN):
            status=self.status()
            if status == 0:
                self.mtk.port.close()
                return True
            else:
                self.error(f"Error on sending shutdown: {self.eh.status(status)}")
        self.mtk.port.close()
        return False

    def getstorage(self, parttype, length):
        if self.daconfig.flashtype == "nor":
            storage = DaStorage.MTK_DA_STORAGE_NOR
        elif self.daconfig.flashtype == "nand":
            storage = DaStorage.MTK_DA_STORAGE_NAND
        elif self.daconfig.flashtype == "ufs":
            storage = DaStorage.MTK_DA_STORAGE_UFS
            if parttype == EMMC_PartitionType.MTK_DA_EMMC_PART_USER:
                parttype = UFS_PartitionType.UFS_LU3
        elif self.daconfig.flashtype == "sdc":
            storage = DaStorage.MTK_DA_STORAGE_SDMMC
        else:
            storage = DaStorage.MTK_DA_STORAGE_EMMC

        part_info = self.partitiontype_and_size(storage, parttype, length)
        return part_info

    def writeflash(self, addr, length, filename, partitionname, offset=0, parttype=None, display=True):
        partinfo = self.getstorage(parttype, length)
        if not partinfo:
            return False
        storage, parttype, length = partinfo
        # self.send_devctrl(self.Cmd.START_DL_INFO)
        plen = self.get_packet_length()
        bytestowrite = length
        write_packet_size = plen.write_packet_length
        if self.cmd_write_data(addr, length, storage, parttype):
            try:
                with open(filename, "rb") as rf:
                    pos = 0
                    rf.seek(offset)
                    while bytestowrite > 0:
                        if display:
                            self.progress.show_progress("Write", length - bytestowrite, length, display)
                        dsize = min(write_packet_size, bytestowrite)
                        data = bytearray(rf.read(dsize))
                        checksum = sum(data) & 0xFFFF
                        dparams = [pack("<I", 0x0), pack("<I", checksum), data]
                        if not self.send_param(dparams):
                            self.error("Error on writing pos 0x%08X" % pos)
                            return False
                        bytestowrite -= dsize
                        pos += dsize
                    status=self.status()
                    if status == 0x0:
                        self.send_devctrl(self.Cmd.CC_OPTIONAL_DOWNLOAD_ACT)
                        self.progress.show_progress("Write", length, length, display)
                        return True
                    else:
                        self.error(f"Error on writeflash: {self.eh.status(status)}")
            except Exception as e:
                self.error(str(e))
                return False
        return False

    def sync(self):
        if self.send(self.Cmd.SYNC_SIGNAL):
            return True
        return False

    def setup_env(self):
        if self.send(self.Cmd.SETUP_ENVIRONMENT):
            da_log_level = 2
            log_channel = 1
            system_os = self.FtSystemOSE.OS_LINUX
            ufs_provision = 0x0
            param = pack("<IIIII", da_log_level, log_channel, system_os, ufs_provision, 0x0)
            if self.send_param(param):
                return True
        return False

    def setup_hw_init(self):
        if self.send(self.Cmd.SETUP_HW_INIT_PARAMS):
            param = pack("<I", 0x0)  # No config
            if self.send_param(param):
                return True
        return False

    def upload(self):
        if self.daconfig.da is None:
            self.error("No valid da loader found... aborting.")
            return False
        loader = self.daconfig.loader
        self.info("Uploading stage 1...")
        with open(loader, 'rb') as bootldr:
            # stage 1
            offset = self.daconfig.da[2]["m_buf"]
            size = self.daconfig.da[2]["m_len"]
            address = self.daconfig.da[2]["m_start_addr"]
            sig_len = self.daconfig.da[2]["m_sig_len"]
            bootldr.seek(offset)
            dadata = bootldr.read(size)
            if self.mtk.preloader.send_da(address, size, sig_len, dadata):
                self.info("Successfully uploaded stage 1, jumping ..")
                if self.mtk.preloader.jump_da(address):
                    sync = self.usbread(1)
                    if sync != b"\xC0":
                        self.error("Error on DA sync")
                        return False
                    else:
                        self.sync()
                        self.setup_env()
                        self.setup_hw_init()
                        res = self.recv()
                        if res == pack("<I", self.Cmd.SYNC_SIGNAL):
                            self.info("Successfully received DA sync")
                            return True
                        else:
                            self.error("Error on jumping to DA: " + hexlify(res).decode('utf-8'))
                else:
                    self.error("Error on jumping to DA.")
            else:
                self.error("Error on sending DA.")
        return False

    def upload_da(self):
        if self.upload():
            self.get_expire_date()
            self.set_reset_key(0x68)
            self.set_battery_opt(0x2)
            self.set_checksum_level(0x0)
            connagent = self.get_connection_agent()
            emmc_info=self.get_emmc_info(False)
            if emmc_info is not None:
                self.info("DRAM config needed for : " + hexlify(emmc_info.cid[:8]).decode('utf-8'))
            # dev_fw_info=self.get_dev_fw_info()
            # dramtype = self.get_dram_type()
            stage = None
            if connagent == b"brom":
                stage = 2
                if self.daconfig.emi is None:
                    self.info("No preloader given. Searching for preloader")
                    found = False
                    for root, dirs, files in os.walk(os.path.join(self.pathconfig.get_loader_path(), 'Preloader')):
                        for file in files:
                            with open(os.path.join(root, file), "rb") as rf:
                                data = rf.read()
                                if emmc_info.cid[:8] in data:
                                    preloader = os.path.join(root, file)
                                    self.daconfig.extract_emi(preloader,False)
                                    if not self.send_emi(self.daconfig.emi):
                                        continue
                                    else:
                                        found = True
                                        self.info("Detected working preloader: " + preloader)
                                        break
                                if found:
                                    break
                    if not found:
                        self.warning("No preloader given. Operation may fail due to missing dram setup.")
                else:
                    if not self.send_emi(self.daconfig.emi):
                        return False
            elif connagent == b"preloader":
                stage = 2
            if stage == 2:
                self.info("Uploading stage 2...")
                with open(self.daconfig.loader, 'rb') as bootldr:
                    stage = stage + 1
                    offset = self.daconfig.da[stage]["m_buf"]
                    size = self.daconfig.da[stage]["m_len"] - self.daconfig.da[stage]["m_sig_len"]
                    address = self.daconfig.da[stage]["m_start_addr"]  # at_address
                    # sig_len = self.daconfig.da[stage]["m_sig_len"]
                    bootldr.seek(offset)
                    da2 = bootldr.read(size)
                    loaded = self.boot_to(address, da2)

                    if loaded:
                        self.info("Successfully uploaded stage 2")
                        self.sram, self.dram = self.get_ram_info()
                        self.emmc = self.get_emmc_info()
                        self.nand = self.get_nand_info()
                        self.nor = self.get_nor_info()
                        self.ufs = self.get_ufs_info()
                        if self.emmc.type != 0:
                            self.daconfig.flashtype = "emmc"
                            self.daconfig.flashsize = self.emmc.user_size
                        elif self.nand.type != 0:
                            self.daconfig.flashtype = "nand"
                            self.daconfig.flashsize = self.nand.total_size
                        elif self.nor.type != 0:
                            self.daconfig.flashtype = "nor"
                            self.daconfig.flashsize = self.nor.available_size
                        elif self.ufs.type != 0:
                            self.daconfig.flashtype = "ufs"
                            self.daconfig.flashsize = [self.ufs.lu0_size, self.ufs.lu1_size, self.ufs.lu2_size]
                        self.chipid = self.get_chip_id()
                        self.randomid = self.get_random_id()
                        # if self.get_da_stor_life_check() == 0x0:
                        cid = self.get_chip_id()
                        self.info("DA-CODE      : 0x%X", (cid.hw_code << 4) + (cid.hw_code >> 4))
                        open(os.path.join("logs", "hwcode.txt"), "w").write(hex(self.config.hwcode))
                        return True
                    else:
                        self.error("Error on booting to da (xflash)")
            else:
                self.error("Didn't get brom connection, got instead: " + hexlify(connagent).decode('utf-8'))
        return False
