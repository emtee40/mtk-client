import hmac
import os
from struct import unpack, pack
from mtkclient.config.payloads import pathconfig
from mtkclient.Library.error import ErrorHandler
from mtkclient.Library.hwcrypto import crypto_setup, hwcrypto
from mtkclient.Library.utils import LogBase, progress, logsetup, find_binary
from mtkclient.Library.settings import hwparam
from mtkclient.Library.seccfg import seccfg
from binascii import hexlify
import hashlib


class XCmd:
    CUSTOM_ACK = 0x0F0000
    CUSTOM_READ = 0x0F0001
    CUSTOM_READREGISTER = 0x0F0002
    CUSTOM_WRITE = 0x0F0003
    CUSTOM_WRITEREGISTER = 0x0F0004
    CUSTOM_INIT_RPMB = 0x0F0005
    CUSTOM_READ_RPMB = 0x0F0006
    CUSTOM_WRITE_RPMB = 0x0F0007
    CUSTOM_INIT_UFS_RPMB = 0x0F0008
    CUSTOM_READ_UFS_RPMB = 0x0F0009
    CUSTOM_WRITE_UFS_RPMB = 0x0F000A


rpmb_error = [
    "",
    "General failure",
    "Authentication failure",
    "Counter failure",
    "Address failure",
    "Write failure",
    "Read failure",
    "Authentication key not yet programmed"
]


class xflashext(metaclass=LogBase):
    def __init__(self, mtk, xflash, loglevel):
        self.pathconfig = pathconfig()
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.error = self.__logger.error
        self.warning = self.__logger.warning
        self.mtk = mtk
        self.loglevel = loglevel
        self.__logger = self.__logger
        self.eh = ErrorHandler()
        self.config = self.mtk.config
        self.usbwrite = self.mtk.port.usbwrite
        self.usbread = self.mtk.port.usbread
        self.echo = self.mtk.port.echo
        self.rbyte = self.mtk.port.rbyte
        self.rdword = self.mtk.port.rdword
        self.rword = self.mtk.port.rword
        self.xflash = xflash
        self.xsend = self.xflash.xsend
        self.send_devctrl = self.xflash.send_devctrl
        self.xread = self.xflash.xread
        self.status = self.xflash.status
        self.hwparam = hwparam(self.mtk.config.meid)
        self.da2 = None
        self.da2address = None

    def patch(self):
        self.da2 = self.xflash.daconfig.da2
        self.da2address = self.xflash.daconfig.da.region[2].m_start_addr  # at_address
        daextensions = os.path.join(self.pathconfig.get_payloads_path(), "da_x.bin")
        if os.path.exists(daextensions):
            daextdata = bytearray(open(daextensions, "rb").read())
            # open("out" + hex(self.da2address) + ".da", "wb").write(da2)
            register_cmd = find_binary(self.da2, b"\x38\xB5\x05\x46\x0C\x20")
            # sec_enc_seccfg = find_binary(self.da2, b"\x0E\x4B\x70\xB5\x06\x46")
            mmc_get_card = find_binary(self.da2, b"\x4B\x4F\xF4\x3C\x72")
            if mmc_get_card is not None:
                mmc_get_card -= 1
            else:
                mmc_get_card = find_binary(self.da2, b"\xA3\xEB\x00\x13\x18\x1A\x02\xEB\x00\x10")
                if mmc_get_card is not None:
                    mmc_get_card -= 10
            pos = 0
            while True:
                mmc_set_part_config = find_binary(self.da2, b"\xC3\x69\x0A\x46\x10\xB5", pos)
                if mmc_set_part_config is None:
                    break
                else:
                    pos = mmc_set_part_config + 1
                    if self.da2[mmc_set_part_config + 20:mmc_set_part_config + 22] == b"\xb3\x21":
                        break
            if mmc_set_part_config is None:
                mmc_set_part_config = find_binary(self.da2, b"\xC3\x69\x13\xF0\x01\x03")
            mmc_rpmb_send_command = find_binary(self.da2, b"\xF8\xB5\x06\x46\x9D\xF8\x18\x50")
            if mmc_rpmb_send_command is None:
                mmc_rpmb_send_command = find_binary(self.da2, b"\x2D\xE9\xF0\x41\x4F\xF6\xFD\x74")

            register_ptr = daextdata.find(b"\x11\x11\x11\x11")
            mmc_get_card_ptr = daextdata.find(b"\x22\x22\x22\x22")
            mmc_set_part_config_ptr = daextdata.find(b"\x33\x33\x33\x33")
            mmc_rpmb_send_command_ptr = daextdata.find(b"\x44\x44\x44\x44")
            ufshcd_queuecommand_ptr = daextdata.find(b"\x55\x55\x55\x55")
            ufshcd_get_free_tag_ptr = daextdata.find(b"\x66\x66\x66\x66")
            ptr_g_ufs_hba_ptr = daextdata.find(b"\x77\x77\x77\x77")

            g_ufs_hba = None
            ptr_g_ufs_hba = find_binary(self.da2, b"\x20\x46\x0B\xB0\xBD\xE8\xF0\x83\x00\xBF")
            if ptr_g_ufs_hba is None:
                ptr_g_ufs_hba = find_binary(self.da2, b"\x21\x46\x02\xF0\x02\xFB\x1B\xE6\x00\xBF")
                if ptr_g_ufs_hba is not None:
                    g_ufs_hba = int.from_bytes(self.da2[ptr_g_ufs_hba + 10 + 0x8:ptr_g_ufs_hba + 10 + 0x8 + 4],
                                               'little')
            else:
                g_ufs_hba = int.from_bytes(self.da2[ptr_g_ufs_hba + 10:ptr_g_ufs_hba + 10 + 4], 'little')
            # open("da2_"+hex(self.da2address)+".bin","wb").write(self.da2)
            if ptr_g_ufs_hba is not None:
                ufshcd_get_free_tag = find_binary(self.da2, b"\xB5.\xB1\x90\xF8")
                ufshcd_queuecommand = find_binary(self.da2, b"\x2D\xE9\xF8\x43\x01\x27")
            else:
                g_ufs_hba = None
                ufshcd_get_free_tag = None
                ufshcd_queuecommand = None

            if register_ptr != -1 and mmc_get_card_ptr != -1:
                if register_cmd:
                    register_cmd = register_cmd + self.da2address | 1
                else:
                    register_cmd = 0
                if mmc_get_card:
                    mmc_get_card = mmc_get_card + self.da2address | 1
                else:
                    mmc_get_card = 0
                if mmc_set_part_config:
                    mmc_set_part_config = mmc_set_part_config + self.da2address | 1
                else:
                    mmc_set_part_config = 0
                if mmc_rpmb_send_command:
                    mmc_rpmb_send_command = mmc_rpmb_send_command + self.da2address | 1
                else:
                    mmc_rpmb_send_command = 0

                if ufshcd_get_free_tag:
                    ufshcd_get_free_tag = ufshcd_get_free_tag + (self.da2address - 1) | 1
                else:
                    ufshcd_get_free_tag = 0

                if ufshcd_queuecommand:
                    ufshcd_queuecommand = ufshcd_queuecommand + self.da2address | 1
                else:
                    ufshcd_queuecommand = 0

                if g_ufs_hba is None:
                    g_ufs_hba = 0

                # Patch the addr
                daextdata[register_ptr:register_ptr + 4] = pack("<I", register_cmd)
                daextdata[mmc_get_card_ptr:mmc_get_card_ptr + 4] = pack("<I", mmc_get_card)
                daextdata[mmc_set_part_config_ptr:mmc_set_part_config_ptr + 4] = pack("<I", mmc_set_part_config)
                daextdata[mmc_rpmb_send_command_ptr:mmc_rpmb_send_command_ptr + 4] = pack("<I", mmc_rpmb_send_command)
                daextdata[ufshcd_get_free_tag_ptr:ufshcd_get_free_tag_ptr + 4] = pack("<I", ufshcd_get_free_tag)
                daextdata[ufshcd_queuecommand_ptr:ufshcd_queuecommand_ptr + 4] = pack("<I", ufshcd_queuecommand)
                daextdata[ptr_g_ufs_hba_ptr:ptr_g_ufs_hba_ptr + 4] = pack("<I", g_ufs_hba)

                # print(hexlify(daextdata).decode('utf-8'))
                # open("daext.bin","wb").write(daextdata)
                return daextdata
        return None

    def patch_da2(self, da2):
        # open("da2.bin","wb").write(da2)
        da2patched = bytearray(da2)
        # Patch security
        is_security_enabled = find_binary(da2, b"\x01\x23\x03\x60\x00\x20\x70\x47")
        if is_security_enabled != -1:
            da2patched[is_security_enabled:is_security_enabled + 2] = b"\x00\x23"
        else:
            self.warning("Security check not patched.")
        # Patch hash check
        authaddr = find_binary(da2, b"\x04\x00\x07\xC0")
        if authaddr:
            da2patched[authaddr:authaddr + 4] = b"\x00\x00\x00\x00"
        elif authaddr is None:
            authaddr = find_binary(da2, b"\x4F\xF0\x04\x09\xCC\xF2\x07\x09")
            if authaddr:
                da2patched[authaddr:authaddr + 8] = b"\x4F\xF0\x00\x09\x4F\xF0\x00\x09"
            else:
                authaddr = find_binary(da2, b"\x4F\xF0\x04\x09\x32\x46\x01\x98\x03\x99\xCC\xF2\x07\x09")
                if authaddr:
                    da2patched[authaddr:authaddr + 14] = b"\x4F\xF0\x00\x09\x32\x46\x01\x98\x03\x99\x4F\xF0\x00\x09"
                else:
                    self.warning("Hash check not patched.")
        # Patch write not allowed
        # open("da2.bin","wb").write(da2patched)
        idx = 0
        patched = False
        while idx != -1:
            idx = da2patched.find(b"\x37\xB5\x00\x23\x04\x46\x02\xA8")
            if idx != -1:
                da2patched[idx:idx + 8] = b"\x37\xB5\x00\x20\x03\xB0\x30\xBD"
                patched = True
            else:
                idx = da2patched.find(b"\x0C\x23\xCC\xF2\x02\x03")
                if idx != -1:
                    da2patched[idx:idx + 6] = b"\x00\x23\x00\x23\x00\x23"
                    idx2 = da2patched.find(b"\x2A\x23\xCC\xF2\x02\x03")
                    if idx2 != -1:
                        da2patched[idx2:idx2 + 6] = b"\x00\x23\x00\x23\x00\x23"
                    """
                    idx3 = da2patched.find(b"\x2A\x24\xE4\xF7\x89\xFB\xCC\xF2\x02\x04")
                    if idx3 != -1:
                        da2patched[idx3:idx3 + 10] = b"\x00\x24\xE4\xF7\x89\xFB\x00\x24\x00\x24"
                    """
                    patched = True
        if not patched:
            self.warning("Write not allowed not patched.")
        return da2patched

    def cmd(self, cmd):
        if self.xsend(self.xflash.Cmd.DEVICE_CTRL):
            status = self.status()
            if status == 0x0:
                if self.xsend(cmd):
                    status = self.status()
                    if status == 0x0:
                        return True
        return False

    def custom_read(self, addr, length):
        if self.cmd(XCmd.CUSTOM_READ):
            self.xsend(addr)
            self.xsend(length)
            data = self.xread()
            status = self.status()
            if status == 0:
                return data
        return b""

    def custom_readregister(self, addr):
        if self.cmd(XCmd.CUSTOM_READREGISTER):
            self.xsend(addr)
            data = self.xread()
            status = self.status()
            if status == 0:
                return data
        return b""

    def custom_write(self, addr, data):
        if self.cmd(XCmd.CUSTOM_WRITE):
            self.xsend(addr)
            self.xsend(len(data))
            self.xsend(data)
            status = self.status()
            if status == 0:
                return True
        return False

    def custom_writeregister(self, addr, data):
        if self.cmd(XCmd.CUSTOM_WRITEREGISTER):
            self.xsend(addr)
            self.xsend(data)
            status = self.status()
            if status == 0:
                return True
        return False

    def readmem(self, addr, dwords=1):
        res = []
        for pos in range(dwords):
            val = self.custom_readregister(addr + pos * 4)
            if val == b"":
                return False
            data = unpack("<I", val)[0]
            if dwords == 1:
                self.debug(f"RX: {hex(addr+(pos*4))} -> " + hex(data))
                return data
            res.append(data)
        self.debug(f"RX: {hex(addr)} -> "+hexlify(b"".join(pack("<I",val) for val in res)).decode('utf-8'))
        return res

    def writeregister(self, addr, dwords):
        if isinstance(dwords, int):
            dwords = [dwords]
        pos = 0
        for val in dwords:
            self.debug(f"TX: {hex(addr+pos)} -> " + hex(val))
            if not self.custom_writeregister(addr + pos, val):
                return False
            pos += 4
        return True

    def writemem(self, addr, data):
        for i in range(0, len(data), 4):
            value = data[i:i + 4]
            while len(value) < 4:
                value += b"\x00"
            self.writeregister(addr + i, unpack("<I", value))
        return True

    def custom_rpmb_read(self, sector, ufs=False):
        cmd = XCmd.CUSTOM_READ_RPMB
        if ufs:
            cmd = XCmd.CUSTOM_READ_UFS_RPMB
        if self.cmd(cmd):
            self.xsend(sector)
            resp = unpack("<H", self.xread())[0]
            if resp == 0x0:
                data = self.xread()
                status = self.status()
                if status == 0:
                    return data
            else:
                self.error(rpmb_error[resp])
                status = self.status()
        return b''

    def custom_rpmb_write(self, sector, data: bytes, ufs=False):
        if len(data) != 0x100:
            self.error("Incorrect rpmb frame length. Aborting")
            return False
        cmd = XCmd.CUSTOM_WRITE_RPMB
        if ufs:
            cmd = XCmd.CUSTOM_WRITE_UFS_RPMB
        if self.cmd(cmd):
            self.xsend(sector)
            self.xsend(data[:0x100])
            resp = unpack("<H", self.xread())[0]
            if resp != 0:
                self.error(rpmb_error[resp])
                status = self.status()
                return False
            status = self.status()
            if status == 0:
                return resp
        return False

    def custom_rpmb_init(self):
        ufs = False
        if self.xflash.emmc.rpmb_size != 0:
            ufs = False
        elif self.xflash.ufs.block_size != 0:
            ufs = True
        cmd = XCmd.CUSTOM_INIT_RPMB
        if ufs:
            cmd = XCmd.CUSTOM_INIT_UFS_RPMB
        if self.cmd(cmd):
            derivedrpmb = self.xread()
            self.info("Derived rpmb key:"+hexlify(derivedrpmb).decode('utf-8'))
            status = self.status()
            if status == 0:
                return True
        return False

    def setotp(self, hwc):
        otp = None
        if self.mtk.config.preloader is not None:
            idx = self.mtk.config.preloader.find(b"\x4D\x4D\x4D\x01\x30")
            if idx != -1:
                otp = self.mtk.config.preloader[idx + 0xC:idx + 0xC + 32]
        if otp is None:
            otp = 32 * b"\x00"
        hwc.sej.sej_set_otp(otp)

    def read_rpmb(self, filename=None, display=True):
        progressbar = progress(1)
        sectors = 0
        ufs = False
        if self.xflash.emmc.rpmb_size != 0:
            sectors = self.xflash.emmc.rpmb_size // 0x100
            ufs = False
        elif self.xflash.ufs.block_size != 0:
            sectors = (512 * 256)
            ufs = True
        if filename is None:
            filename = "rpmb.bin"
            if sectors > 0:
                with open(filename, "wb") as wf:
                    for sector in range(sectors):
                        if display:
                            progressbar.show_progress("RPMB read", sector, sectors, display)
                        data = self.custom_rpmb_read(sector=sector, ufs=ufs)
                        if data == b"":
                            self.error("Couldn't read rpmb.")
                            return False
                        wf.write(data)
                self.info("Done reading rpmb to " + filename)
                return True
        return False

    def write_rpmb(self, filename=None, display=True):
        progressbar = progress(1)
        if filename is None:
            self.error("Filename has to be given for writing to rpmb")
            return False
        if not os.path.exists(filename):
            self.error(f"Couldn't find {filename} for writing to rpmb.")
            return False
        ufs = False
        sectors = 0
        if self.xflash.emmc.rpmb_size != 0:
            sectors = self.xflash.emmc.rpmb_size // 0x100
        elif self.xflash.ufs.block_size != 0:
            sectors = (512 * 256)
        if self.custom_rpmb_init():
            if sectors > 0:
                with open(filename, "rb") as rf:
                    for sector in range(sectors):
                        if display:
                            progressbar.show_progress("RPMB written", sector, sectors, display)
                        if not self.custom_rpmb_write(sector=sector, data=rf.read(0x100), ufs=ufs):
                            self.error(f"Couldn't write rpmb at sector {sector}.")
                            return False
                self.info(f"Done reading writing {filename} to rpmb")
                return True
        return False

    def erase_rpmb(self, display=True):
        progressbar = progress(1)
        ufs = False
        sectors = 0
        if self.xflash.emmc.rpmb_size != 0:
            sectors = self.xflash.emmc.rpmb_size // 0x100
        elif self.xflash.ufs.block_size != 0:
            sectors = (512 * 256)
        if self.custom_rpmb_init():
            if sectors > 0:
                for sector in range(sectors):
                    if display:
                        progressbar.show_progress("RPMB erased", sector, sectors, display)
                    if not self.custom_rpmb_write(sector=sector, data=b"\x00" * 0x100, ufs=ufs):
                        self.error(f"Couldn't erase rpmb at sector {sector}.")
                        return False
                self.info(f"Done erasing rpmb")
                return True
        return False

    def cryptosetup(self):
        setup = crypto_setup()
        setup.blacklist = self.config.chipconfig.blacklist
        setup.gcpu_base = self.config.chipconfig.gcpu_base
        setup.dxcc_base = self.config.chipconfig.dxcc_base
        setup.da_payload_addr = self.config.chipconfig.da_payload_addr
        setup.sej_base = self.config.chipconfig.sej_base
        setup.read32 = self.readmem
        setup.write32 = self.writeregister
        setup.writemem = self.writemem
        return hwcrypto(setup, self.loglevel, self.config.gui)

    def seccfg(self, lockflag):
        if lockflag not in ["unlock", "lock"]:
            print("Valid flags are: unlock, lock")
            return False
        hwc = self.cryptosetup()
        sc_org = seccfg(hwc)
        data, guid_gpt = self.xflash.partition.get_gpt(self.mtk.config.gpt_settings, "user")
        seccfg_data = None
        partition = None
        if guid_gpt is None:
            self.error("Error getting the partition table.")
            return False
        for rpartition in guid_gpt.partentries:
            if rpartition.name == "seccfg":
                partition = rpartition
                seccfg_data = self.xflash.readflash(
                    addr=partition.sector * self.mtk.daloader.daconfig.pagesize,
                    length=partition.sectors * self.mtk.daloader.daconfig.pagesize,
                    filename="", parttype="user", display=False)
                break
        if seccfg_data is None:
            self.error("Couldn't detect existing seccfg partition. Aborting unlock.")
            return False
        if seccfg_data[:4] != pack("<I", 0x4D4D4D4D):
            self.error("Unknown seccfg partition header. Aborting unlock.")
            return False

        if not sc_org.parse(seccfg_data):
            return False
        sc_new = seccfg(hwc)
        self.setotp(hwc)
        hwtype = "hw"
        V3 = True
        sc_new.create(sc_org=sc_org, hwtype=hwtype, V3=V3)
        if sc_org.hash != sc_new.hash:
            V3 = False
            sc_new.create(sc_org=sc_org, hwtype=hwtype, V3=V3)
        if sc_org.hash != sc_new.hash:
            hwtype = "sw"
            sc_new.create(sc_org=sc_org, hwtype=hwtype)
            if sc_org.hash != sc_new.hash:
                self.error("Device has is either already unlocked or algo is unknown. Aborting.")
                return False
        writedata = sc_new.create(sc_org=None, hwtype=hwtype, lockflag=lockflag, V3=V3)
        if self.xflash.writeflash(addr=partition.sector * self.mtk.daloader.daconfig.pagesize,
                                  length=len(writedata),
                                  filename=None, wdata=writedata, parttype="user", display=True):
            self.info("Successfully wrote seccfg.")
            return True
        self.error("Error on writing seccfg config to flash.")
        return False

    def generate_keys(self):
        hwc = self.cryptosetup()
        meid = b""
        meidv = self.hwparam.loadsetting("meid")
        socidv = self.hwparam.loadsetting("socid")
        if meidv is not None:
            meid = bytes.fromhex(meidv)
            self.info("MEID        : " + meidv)
        else:
            try:
                if self.config.chipconfig.meid_addr is not None:
                    meid = b"".join([pack("<I", val) for val in self.readmem(self.config.chipconfig.meid_addr, 4)])
                    self.hwparam.writesetting("meid", hexlify(meid).decode('utf-8'))
                    self.info("MEID        : " + hexlify(meid).decode('utf-8'))
            except Exception as err:
                pass
        if socidv is not None:
            socid = bytes.fromhex(socidv)
            self.info("SOCID        : " + socidv)
        else:
            try:
                if self.config.chipconfig.socid_addr is not None:
                    socid = b"".join([pack("<I", val) for val in self.readmem(self.config.chipconfig.socid_addr, 8)])
                    self.hwparam.writesetting("socid", hexlify(socid).decode('utf-8'))
                    self.info("SOCID        : " + hexlify(socid).decode('utf-8'))
            except Exception as err:
                pass

        if self.config.chipconfig.dxcc_base is not None:
            #hwc.aes_hwcrypt(btype="gcpu", mode="mtee")
            self.info("Generating dxcc rpmbkey...")
            rpmbkey = hwc.aes_hwcrypt(btype="dxcc", mode="rpmb")
            self.info("Generating dxcc fdekey...")
            fdekey = hwc.aes_hwcrypt(btype="dxcc", mode="fde")
            self.info("Generating dxcc rpmbkey2...")
            rpmb2key = hwc.aes_hwcrypt(btype="dxcc", mode="rpmb2")
            self.info("Generating dxcc km key...")
            ikey = hwc.aes_hwcrypt(btype="dxcc", mode="itrustee")
            # self.info("Generating dxcc platkey + provkey key...")
            # platkey, provkey = hwc.aes_hwcrypt(btype="dxcc", mode="prov")
            # self.info("Provkey     : " + hexlify(provkey).decode('utf-8'))
            # self.info("Platkey     : " + hexlify(platkey).decode('utf-8'))
            if rpmbkey is not None:
                self.info("RPMB        : " + hexlify(rpmbkey).decode('utf-8'))
                self.hwparam.writesetting("rpmbkey", hexlify(rpmbkey).decode('utf-8'))
            if rpmb2key is not None:
                self.info("RPMB2       : " + hexlify(rpmb2key).decode('utf-8'))
                self.hwparam.writesetting("rpmb2key", hexlify(rpmb2key).decode('utf-8'))
            if fdekey is not None:
                self.info("FDE         : " + hexlify(fdekey).decode('utf-8'))
                self.hwparam.writesetting("fdekey", hexlify(fdekey).decode('utf-8'))
            if ikey is not None:
                self.info("iTrustee    : " + hexlify(ikey).decode('utf-8'))
                self.hwparam.writesetting("kmkey", hexlify(ikey).decode('utf-8'))
            if self.config.chipconfig.prov_addr:
                provkey = self.custom_read(self.config.chipconfig.prov_addr, 16)
                self.info("PROV        : " + hexlify(provkey).decode('utf-8'))
                self.hwparam.writesetting("provkey", hexlify(provkey).decode('utf-8'))
            """
            hrid = self.xflash.get_hrid()
            if hrid is not None:
                self.info("HRID        : " + hexlify(hrid).decode('utf-8'))
                open(os.path.join("logs", "hrid.txt"), "wb").write(hexlify(hrid))
            """
            return {"rpmb": hexlify(rpmbkey).decode('utf-8'),"rpmb2":hexlify(rpmb2key).decode('utf-8'),"fde":hexlify(fdekey).decode('utf-8'),"ikey":hexlify(ikey).decode('utf-8')}
        elif self.config.chipconfig.sej_base is not None:
            if meid == b"":
                if self.config.chipconfig.meid_addr:
                    meid = self.custom_read(self.config.chipconfig.meid_addr, 16)
            if meid != b"":
                self.info("Generating sej rpmbkey...")
                self.setotp(hwc)
                rpmbkey = hwc.aes_hwcrypt(mode="rpmb", data=meid, btype="sej")
                self.info("RPMB        : " + hexlify(rpmbkey).decode('utf-8'))
                self.hwparam.writesetting("rpmbkey", hexlify(rpmbkey).decode('utf-8'))
            else:
                self.info("SEJ Mode: No meid found. Are you in brom mode ?")
        return True
