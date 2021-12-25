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

class LCmd:
    CUSTOM_READ = b"\x29"
    CUSTOM_WRITE = b"\x2A"
    ACK = b"\x5A"
    NACK = b"\xA5"

class legacyext(metaclass=LogBase):
    def __init__(self, mtk, legacy, loglevel):
        self.pathconfig = pathconfig()
        self.__logger = logsetup(self, self.__logger, loglevel, mtk.config.gui)
        self.info = self.__logger.info
        self.debug = self.__logger.debug
        self.error = self.__logger.error
        self.warning = self.__logger.warning
        self.mtk = mtk
        self.hwparam = hwparam(mtk.config.meid)
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
        self.legacy = legacy
        self.Cmd=LCmd()
        self.da2 = None
        self.da2address = None

    def patch_da2(self, da2):
        da2patched = bytearray(da2)
        # Patch security
        check_addr = find_binary(da2, b"\x08\xB5\x4F\xF4\x50\x42\xA0\xF1\x81\x53")
        if check_addr is not None:
            da2patched[check_addr:check_addr + 6] = b"\x08\xB5\x00\x20\x08\xBD"
        else:
            self.warning("Legacy address check not patched.")
        return da2patched

    def fix_hash(self, da1, da2, da2sig_len, hashpos, hashmode):
        da1 = bytearray(da1)
        dahash = None
        if hashmode == 1:
            dahash = hashlib.sha1(da2[:-da2sig_len]).digest()
        elif hashmode == 2:
            dahash = hashlib.sha256(da2[:-da2sig_len]).digest()
        da1[hashpos:hashpos + len(dahash)] = dahash
        return da1

    def readmem(self, addr, dwords=1):
        res = []
        for pos in range(dwords):
            data = self.legacy.read_reg32(addr + pos * 4)
            if data is None:
                return False
            if dwords == 1:
                return data
            res.append(data)
        return res

    def custom_read(self, addr, length):
        dwords=length//4
        if length%4!=0:
            dwords+=1
        data = b"".join([pack(">I",val) for val in self.readmem(addr, dwords)])
        return data[:length]

    def writeregister(self, addr, dwords):
        if isinstance(dwords, int):
            dwords = [dwords]
        pos = 0
        for val in dwords:
            if not self.legacy.write_reg32(addr + pos, val):
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

    def custom_write(self, addr, data):
        return self.writemem(addr, data)

    def setotp(self, hwc):
        otp = None
        if self.mtk.config.preloader is not None:
            idx = self.mtk.config.preloader.find(b"\x4D\x4D\x4D\x01\x30")
            if idx != -1:
                otp = self.mtk.config.preloader[idx + 0xC:idx + 0xC + 32]
        if otp is None:
            otp = 32 * b"\x00"
        hwc.sej.sej_set_otp(otp)

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
        data, guid_gpt = self.legacy.partition.get_gpt(self.mtk.config.gpt_settings, "user")
        seccfg_data = None
        partition = None
        for rpartition in guid_gpt.partentries:
            if rpartition.name == "seccfg":
                partition = rpartition
                seccfg_data = self.legacy.readflash(
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
            V3=False
            sc_new.create(sc_org=sc_org, hwtype=hwtype, V3=V3)
        if sc_org.hash != sc_new.hash:
            hwtype = "sw"
            sc_new.create(sc_org=sc_org, hwtype=hwtype)
            if sc_org.hash != sc_new.hash:
                self.error("Device has is either already unlocked or algo is unknown. Aborting.")
                return False
        writedata = sc_new.create(sc_org=None, hwtype=hwtype, lockflag=lockflag, V3=V3)
        if self.legacy.writeflash(addr=partition.sector * self.mtk.daloader.daconfig.pagesize,
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
                    socid = b"".join([pack("<I",val) for val in self.readmem(self.config.chipconfig.socid_addr,8)])
                    self.hwparam.writesetting("socid", hexlify(socid).decode('utf-8'))
                    self.info("SOCID        : " + hexlify(socid).decode('utf-8'))
            except Exception as err:
                pass
        if self.config.chipconfig.dxcc_base is not None:
            self.info("Generating dxcc rpmbkey...")
            rpmbkey = hwc.aes_hwcrypt(btype="dxcc", mode="rpmb")
            self.info("Generating dxcc fdekey...")
            fdekey = hwc.aes_hwcrypt(btype="dxcc", mode="fde")
            self.info("Generating dxcc rpmbkey2...")
            rpmb2key = hwc.aes_hwcrypt(btype="dxcc", mode="rpmb2")
            self.info("Generating dxcc km key...")
            ikey = hwc.aes_hwcrypt(btype="dxcc", mode="itrustee")
            #self.info("Generating dxcc platkey + provkey key...")
            #platkey, provkey = hwc.aes_hwcrypt(btype="dxcc", mode="prov")
            #self.info("Provkey     : " + hexlify(provkey).decode('utf-8'))
            #self.info("Platkey     : " + hexlify(platkey).decode('utf-8'))
            if rpmbkey is not None:
                self.info("RPMB        : " + hexlify(rpmbkey).decode('utf-8'))
                self.hwparam.writesetting("rpmbkey",hexlify(rpmbkey).decode('utf-8'))
            if rpmb2key is not None:
                self.info("RPMB2       : " + hexlify(rpmb2key).decode('utf-8'))
                self.hwparam.writesetting("rpmb2key",hexlify(rpmb2key).decode('utf-8'))
            if fdekey is not None:
                self.info("FDE         : " + hexlify(fdekey).decode('utf-8'))
                self.hwparam.writesetting("fdekey",hexlify(fdekey).decode('utf-8'))
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
        elif self.config.chipconfig.sej_base is not None:
            if meid == b"":
                if self.config.chipconfig.meid_addr:
                    meid = self.custom_read(self.config.chipconfig.meid_addr,16)
            if meid != b"":
                self.info("Generating sej rpmbkey...")
                self.setotp(hwc)
                rpmbkey = hwc.aes_hwcrypt(mode="rpmb", data=meid, btype="sej")
                self.info("RPMB        : " + hexlify(rpmbkey).decode('utf-8'))
                self.hwparam.writesetting("rpmbkey", hexlify(rpmbkey).decode('utf-8'))
            else:
                self.info("SEJ Mode: No meid found. Are you in brom mode ?")
        return True
