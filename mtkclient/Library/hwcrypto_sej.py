#!/usr/bin/python3
# -*- coding: utf-8 -*-
# (c) B.Kerler 2018-2021 GPLv3 License
import logging, os
from struct import pack, unpack
from mtkclient.Library.utils import LogBase

CustomSeed = bytearray(b"12abcdef")

# SEJ = Security Engine for JTAG protection

def bytes_to_dwords(buf):
    res = []
    for i in range(0, len(buf) // 4):
        res.append(unpack("<I", buf[i * 4:(i * 4) + 4])[0])
    return res


AES_CBC_MODE = 1
AES_SW_KEY = 0
AES_HW_KEY = 1
AES_HW_WRAP_KEY = 2
AES_KEY_128 = 16
AES_KEY_256 = 32

regval = {
    "HACC_CON": 0x0000,
    "HACC_ACON": 0x0004,
    "HACC_ACON2": 0x0008,
    "HACC_ACONK": 0x000C,
    "HACC_ASRC0": 0x0010,
    "HACC_ASRC1": 0x0014,
    "HACC_ASRC2": 0x0018,
    "HACC_ASRC3": 0x001C,
    "HACC_AKEY0": 0x0020,
    "HACC_AKEY1": 0x0024,
    "HACC_AKEY2": 0x0028,
    "HACC_AKEY3": 0x002C,
    "HACC_AKEY4": 0x0030,
    "HACC_AKEY5": 0x0034,
    "HACC_AKEY6": 0x0038,
    "HACC_AKEY7": 0x003C,
    "HACC_ACFG0": 0x0040,
    "HACC_ACFG1": 0x0044,
    "HACC_ACFG2": 0x0048,
    "HACC_ACFG3": 0x004C,
    "HACC_AOUT0": 0x0050,
    "HACC_AOUT1": 0x0054,
    "HACC_AOUT2": 0x0058,
    "HACC_AOUT3": 0x005C,
    "HACC_SW_OTP0": 0x0060,
    "HACC_SW_OTP1": 0x0064,
    "HACC_SW_OTP2": 0x0068,
    "HACC_SW_OTP3": 0x006c,
    "HACC_SW_OTP4": 0x0070,
    "HACC_SW_OTP5": 0x0074,
    "HACC_SW_OTP6": 0x0078,
    "HACC_SW_OTP7": 0x007c,
    "HACC_SECINIT0": 0x0080,
    "HACC_SECINIT1": 0x0084,
    "HACC_SECINIT2": 0x0088,
    "HACC_MKJ": 0x00a0,
    "HACC_UNK": 0x00bc
}


class hacc_reg:
    def __init__(self, setup):
        self.sej_base = setup.sej_base
        self.read32 = setup.read32
        self.write32 = setup.write32

    def __setattr__(self, key, value):
        if key in ("sej_base", "read32", "write32", "regval"):
            return super(hacc_reg, self).__setattr__(key, value)
        if key in regval:
            addr = regval[key] + self.sej_base
            return self.write32(addr, value)
        else:
            return super(hacc_reg, self).__setattr__(key, value)

    def __getattribute__(self, item):
        if item in ("sej_base", "read32", "write32", "regval"):
            return super(hacc_reg, self).__getattribute__(item)
        if item in regval:
            addr = regval[item] + self.sej_base
            return self.read32(addr)
        else:
            return super(hacc_reg, self).__getattribute__(item)


class sej(metaclass=LogBase):
    encrypt = True

    HACC_AES_DEC = 0x00000000
    HACC_AES_ENC = 0x00000001
    HACC_AES_MODE_MASK = 0x00000002
    HACC_AES_ECB = 0x00000000
    HACC_AES_CBC = 0x00000002
    HACC_AES_TYPE_MASK = 0x00000030
    HACC_AES_128 = 0x00000000
    HACC_AES_192 = 0x00000010
    HACC_AES_256 = 0x00000020
    HACC_AES_CHG_BO_MASK = 0x00001000
    HACC_AES_CHG_BO_OFF = 0x00000000
    HACC_AES_CHG_BO_ON = 0x00001000
    HACC_AES_START = 0x00000001
    HACC_AES_CLR = 0x00000002
    HACC_AES_RDY = 0x00008000

    HACC_AES_BK2C = 0x00000010
    HACC_AES_R2K = 0x00000100

    HACC_SECINIT0_MAGIC = 0xAE0ACBEA
    HACC_SECINIT1_MAGIC = 0xCD957018
    HACC_SECINIT2_MAGIC = 0x46293911

    # This seems to be fixed
    g_CFG_RANDOM_PATTERN = [
        0x2D44BB70,
        0xA744D227,
        0xD0A9864B,
        0x83FFC244,
        0x7EC8266B,
        0x43E80FB2,
        0x01A6348A,
        0x2067F9A0,
        0x54536405,
        0xD546A6B1,
        0x1CC3EC3A,
        0xDE377A83
    ]

    g_HACC_CFG_1 = [
        0x9ED40400, 0x00E884A1, 0xE3F083BD, 0x2F4E6D8A,
        0xFF838E5C, 0xE940A0E3, 0x8D4DECC6, 0x45FC0989
    ]

    g_HACC_CFG_2 = [
        0xAA542CDA, 0x55522114, 0xE3F083BD, 0x55522114,
        0xAA542CDA, 0xAA542CDA, 0x55522114, 0xAA542CDA
    ]

    g_HACC_CFG_3 = [
        0x2684B690, 0xEB67A8BE, 0xA113144C, 0x177B1215,
        0x168BEE66, 0x1284B684, 0xDF3BCE3A, 0x217F6FA2
    ]

    g_HACC_CFG_MTEE = [
        0x9ED40400, 0xE884A1, 0xE3F083BD, 0x2F4E6D8A
    ]

    def __init__(self, setup, loglevel=logging.INFO):
        self.__logger = self.__logger
        self.hwcode = setup.hwcode
        self.reg = hacc_reg(setup)
        # mediatek,hacc, mediatek,sej
        self.sej_base = setup.sej_base
        self.read32 = setup.read32
        self.write32 = setup.write32
        self.info = self.__logger.info
        self.error = self.__logger.error
        self.warning = self.__logger.warning
        if loglevel == logging.DEBUG:
            logfilename = os.path.join("logs", "log.txt")
            fh = logging.FileHandler(logfilename, encoding='utf-8')
            self.__logger.addHandler(fh)
            self.__logger.setLevel(logging.DEBUG)
        else:
            self.__logger.setLevel(logging.INFO)

    def uffs(self, x):
        v1 = x
        if x & 0xFFFF:
            result = 1
        else:
            v1 >>= 16
            result = 17
        if not v1 & 0xFF:
            v1 >>= 8
            result += 8
        if not ((v1 << 28) & 0xFFFFFFFF):
            v1 >>= 4
            result += 4
        if not ((v1 << 30) & 0xFFFFFFFF):
            v1 >>= 2
            result += 2
        if not v1 & 1:
            result += 1
        return result

    def tz_dapc_set_master_transaction(self, master_index, permission_control):
        t = 1 << master_index
        v = self.read32(0x10007500) & ~t
        if t:
            t = self.uffs(t)
        val = v | permission_control << (t - 1)
        self.write32(0x10007500, val)
        return t

    def crypto_secure(self, val):
        if val:
            self.write32(0x10216024, 0x20002)
        else:
            self.write32(0x10216024, 0x0)

    def device_APC_dom_setup(self):
        self.write32(0x10007F00, 0)
        tv = self.read32(0x10007400) & 0xFFFFFFFF
        self.write32(0x10007400, tv | (1 << (self.uffs(0xF0000000) - 1)))
        tv_0 = self.read32(0x10007400) & 0xF0FFFFFF
        self.write32(0x10007400, tv | (2 << (self.uffs(0xF0000000) - 1)))

    def sej_set_mode(self, mode):
        self.reg.HACC_ACON = self.reg.HACC_ACON & ((~2) & 0xFFFFFFFF)
        if mode == 1:  # CBC
            self.reg.HACC_ACON |= 2

    def sej_set_key(self, key, flag, data=None):
        # 0 uses software key (sml_aes_key)
        # 1 uses Real HW Crypto Key
        # 2 uses 32 byte hw derived key from sw key
        # 3 uses 32 byte hw derived key from rid
        # 4 uses custom key (customer key ?)
        klen = 0x10
        if flag == 0x18:
            klen = 0x10
        elif flag == 0x20:
            klen = 0x20
        self.write32(0x109E64, klen)
        self.reg.HACC_ACON = (self.reg.HACC_ACON & 0xFFFFFFCF) | klen
        self.reg.HACC_AKEY0 = 0
        self.reg.HACC_AKEY1 = 0
        self.reg.HACC_AKEY2 = 0
        self.reg.HACC_AKEY3 = 0
        self.reg.HACC_AKEY4 = 0
        self.reg.HACC_AKEY5 = 0
        self.reg.HACC_AKEY6 = 0
        self.reg.HACC_AKEY7 = 0

        if key == 1:
            self.reg.HACC_ACONK |= 0x10
        else:
            # Key has to be converted to be big endian
            keydata = [0, 0, 0, 0, 0, 0, 0, 0]
            for i in range(0, len(data), 4):
                keydata[i // 4] = unpack(">I", data[i:i + 4])[0]
            self.reg.HACC_AKEY0 = keydata[0]
            self.reg.HACC_AKEY1 = keydata[1]
            self.reg.HACC_AKEY2 = keydata[2]
            self.reg.HACC_AKEY3 = keydata[3]
            self.reg.HACC_AKEY4 = keydata[4]
            self.reg.HACC_AKEY5 = keydata[5]
            self.reg.HACC_AKEY6 = keydata[6]
            self.reg.HACC_AKEY7 = keydata[7]

    def tz_pre_init(self):
        # self.device_APC_dom_setup()
        # self.tz_dapc_set_master_transaction(4,1)
        # self.crypto_secure(1)
        return

    def SEJ_Init_MTEE(self, encrypt=True, iv=None):
        if iv is None:
            iv = self.g_HACC_CFG_MTEE
        acon_setting = self.HACC_AES_CHG_BO_OFF | self.HACC_AES_CBC | self.HACC_AES_128
        if encrypt:
            acon_setting |= self.HACC_AES_ENC
        else:
            acon_setting |= self.HACC_AES_DEC

        # clear key
        self.reg.HACC_AKEY0 = 0
        self.reg.HACC_AKEY1 = 0
        self.reg.HACC_AKEY2 = 0
        self.reg.HACC_AKEY3 = 0
        self.reg.HACC_AKEY4 = 0
        self.reg.HACC_AKEY5 = 0
        self.reg.HACC_AKEY6 = 0
        self.reg.HACC_AKEY7 = 0

        self.reg.HACC_ACON2 = self.HACC_AES_CBC
        self.reg.HACC_ACONK = self.HACC_AES_BK2C
        self.reg.HACC_ACONK |= 0x100
        self.reg.HACC_ACON = self.HACC_AES_CLR

        self.reg.HACC_ACFG0 = iv[0]
        self.reg.HACC_ACFG1 = iv[1]
        self.reg.HACC_ACFG2 = iv[2]
        self.reg.HACC_ACFG3 = iv[3]

        for val in [[0x2d44bb70,0xa744d227,0xd0a9864b,0x83ffc244],
                    [0x7ec8266b,0x43e80fb2,0x1a6348a,0x2067f9a0],
                    [0x54536405,0xd546a6b1,0x1cc3ec3a,0xde377a83]]:
            self.reg.HACC_ASRC0 = val[0]
            self.reg.HACC_ASRC1 = val[1]
            self.reg.HACC_ASRC2 = val[2]
            self.reg.HACC_ASRC3 = val[3]
            self.reg.HACC_ACON2 = self.HACC_AES_START
            i = 0
            while i < 20:
                if self.reg.HACC_ACON2 & self.HACC_AES_RDY != 0:
                    break
                i += 1
            if i == 20:
                self.error("SEJ Hardware seems not to be configured correctly. Results may be wrong.")

        self.reg.HACC_ACON2 = self.HACC_AES_CBC
        self.reg.HACC_ACFG0 = iv[0]
        self.reg.HACC_ACFG1 = iv[1]
        self.reg.HACC_ACFG2 = iv[2]
        self.reg.HACC_ACFG3 = iv[3]
        self.reg.HACC_ACON  = acon_setting
        self.reg.HACC_ACONK = 0x0

    def SEJ_Init(self, encrypt=True, iv=None):
        if iv is None:
            iv = self.g_HACC_CFG_1
        acon_setting = self.HACC_AES_CHG_BO_OFF | self.HACC_AES_CBC | self.HACC_AES_128
        if encrypt:
            acon_setting |= self.HACC_AES_ENC
        else:
            acon_setting |= self.HACC_AES_DEC

        # clear key
        self.reg.HACC_AKEY0 = 0
        self.reg.HACC_AKEY1 = 0
        self.reg.HACC_AKEY2 = 0
        self.reg.HACC_AKEY3 = 0
        self.reg.HACC_AKEY4 = 0
        self.reg.HACC_AKEY5 = 0
        self.reg.HACC_AKEY6 = 0
        self.reg.HACC_AKEY7 = 0
        self.reg.HACC_ACFG0 = iv[0]  # g_AC_CFG
        self.reg.HACC_ACFG1 = iv[1]
        self.reg.HACC_ACFG2 = iv[2]
        self.reg.HACC_ACFG3 = iv[3]
        self.reg.HACC_UNK |= 2

        # clear HACC_ASRC/HACC_ACFG/HACC_AOUT
        self.reg.HACC_ACON2 = 0x40000000 | self.HACC_AES_CLR

        while True:
            if self.reg.HACC_ACON2 > 0x80000000:
                break

        self.reg.HACC_UNK &= 0xFFFFFFFE
        self.reg.HACC_ACONK = self.HACC_AES_BK2C
        self.reg.HACC_ACON = acon_setting
        return acon_setting

    def SEJ_Run(self, data):
        pdst = bytearray()
        psrc = bytes_to_dwords(data)
        plen = len(psrc)
        pos = 0
        for i in range(plen // 4):
            self.reg.HACC_ASRC0 = psrc[pos + 0]
            self.reg.HACC_ASRC1 = psrc[pos + 1]
            self.reg.HACC_ASRC2 = psrc[pos + 2]
            self.reg.HACC_ASRC3 = psrc[pos + 3]
            self.reg.HACC_ACON2 = self.HACC_AES_START
            i = 0
            while i < 20:
                if self.reg.HACC_ACON2 & self.HACC_AES_RDY != 0:
                    break
                i += 1
            if i == 20:
                self.error("SEJ Hardware seems not to be configured correctly. Results may be wrong.")
            pdst.extend(pack("<I", self.reg.HACC_AOUT0))
            pdst.extend(pack("<I", self.reg.HACC_AOUT1))
            pdst.extend(pack("<I", self.reg.HACC_AOUT2))
            pdst.extend(pack("<I", self.reg.HACC_AOUT3))
            pos += 4
        return pdst

    def SEJ_Terminate(self):
        self.reg.HACC_ACON2 = self.HACC_AES_CLR
        self.reg.HACC_AKEY0 = 0
        self.reg.HACC_AKEY1 = 0
        self.reg.HACC_AKEY2 = 0
        self.reg.HACC_AKEY3 = 0
        self.reg.HACC_AKEY4 = 0
        self.reg.HACC_AKEY5 = 0
        self.reg.HACC_AKEY6 = 0
        self.reg.HACC_AKEY7 = 0

    def SEJ_V3_Init(self, ben=True, iv=None):
        if iv is None:
            iv = self.g_HACC_CFG_1
        acon_setting = self.HACC_AES_CHG_BO_OFF | self.HACC_AES_CBC | self.HACC_AES_128
        if ben:
            acon_setting |= self.HACC_AES_ENC
        else:
            acon_setting |= self.HACC_AES_DEC

        # clear key
        self.reg.HACC_AKEY0 = 0  # 0x20
        self.reg.HACC_AKEY1 = 0
        self.reg.HACC_AKEY2 = 0
        self.reg.HACC_AKEY3 = 0
        self.reg.HACC_AKEY4 = 0
        self.reg.HACC_AKEY5 = 0
        self.reg.HACC_AKEY6 = 0
        self.reg.HACC_AKEY7 = 0  # 0x3C

        # Generate META Key # 0x04
        self.reg.HACC_ACON = self.HACC_AES_CHG_BO_OFF | self.HACC_AES_CBC | self.HACC_AES_128 | self.HACC_AES_DEC

        # init ACONK, bind HUID/HUK to HACC, this may differ
        # enable R2K, so that output data is feedback to key by HACC internal algorithm
        self.reg.HACC_ACONK = self.HACC_AES_BK2C | self.HACC_AES_R2K  # 0x0C

        # clear HACC_ASRC/HACC_ACFG/HACC_AOUT
        self.reg.HACC_ACON2 = self.HACC_AES_CLR  # 0x08
        self.reg.HACC_UNK = 1
        self.reg.HACC_ACFG0 = iv[0]  # g_AC_CFG
        self.reg.HACC_ACFG1 = iv[1]
        self.reg.HACC_ACFG2 = iv[2]
        self.reg.HACC_ACFG3 = iv[3]

        # encrypt fix pattern 3 rounds to generate a pattern from HUID/HUK
        for i in range(0, 3):
            pos = i * 4
            self.reg.HACC_ASRC0 = self.g_CFG_RANDOM_PATTERN[pos]
            self.reg.HACC_ASRC1 = self.g_CFG_RANDOM_PATTERN[pos + 1]
            self.reg.HACC_ASRC2 = self.g_CFG_RANDOM_PATTERN[pos + 2]
            self.reg.HACC_ASRC3 = self.g_CFG_RANDOM_PATTERN[pos + 3]
            self.reg.HACC_ACON2 = self.HACC_AES_START
            i = 0
            while i < 20:
                if self.reg.HACC_ACON2 & self.HACC_AES_RDY != 0:
                    break
                i += 1
            if i == 20:
                self.error("SEJ Hardware seems not to be configured correctly. Results may be wrong.")
        self.reg.HACC_ACON2 = self.HACC_AES_CLR
        self.reg.HACC_ACFG0 = iv[0]
        self.reg.HACC_ACFG1 = iv[1]
        self.reg.HACC_ACFG2 = iv[2]
        self.reg.HACC_ACFG3 = iv[3]
        self.reg.HACC_ACON = acon_setting
        self.reg.HACC_ACONK = 0

    def hw_aes128_cbc_encrypt(self, buf, encrypt=True, iv=None):
        if iv is None:
            iv = self.g_HACC_CFG_1
        self.tz_pre_init()
        self.info("HACC init")
        self.SEJ_V3_Init(ben=encrypt, iv=iv)
        self.info("HACC run")
        buf2 = self.SEJ_Run(buf)
        self.info("HACC terminate")
        self.SEJ_Terminate()
        return buf2

    def hw_aes128_sst_encrypt(self, buf, encrypt=True):
        seed = (CustomSeed[2]<<16) | (CustomSeed[1]<<8) | CustomSeed[0] | (CustomSeed[3]<<24)
        iv = [seed,(~seed)&0xFFFFFFFF,(((seed>>16)|(seed<<16))&0xFFFFFFFF),(~((seed>>16)|(seed<<16))&0xFFFFFFFF)]

        self.tz_pre_init()
        self.info("HACC init")
        self.SEJ_Init(encrypt=encrypt, iv=iv)
        self.info("HACC run")
        buf2 = self.SEJ_Run(buf)
        self.info("HACC terminate")
        self.SEJ_Terminate()
        return buf2

    def sej_set_otp(self, data):
        pd = bytes_to_dwords(data)
        self.reg.HACC_SW_OTP0 = pd[0]
        self.reg.HACC_SW_OTP1 = pd[1]
        self.reg.HACC_SW_OTP2 = pd[2]
        self.reg.HACC_SW_OTP3 = pd[3]
        self.reg.HACC_SW_OTP4 = pd[4]
        self.reg.HACC_SW_OTP5 = pd[5]
        self.reg.HACC_SW_OTP6 = pd[6]
        self.reg.HACC_SW_OTP7 = pd[7]
        # self.reg.HACC_SECINIT0 = pd[8]
        # self.reg.HACC_SECINIT1 = pd[9]
        # self.reg.HACC_SECINIT2 = pd[0xA]
        # self.reg.HACC_MKJ = pd[0xB]

    def sej_do_aes(self, encrypt, iv=None, data=b"", length=16):
        self.reg.HACC_ACON2 |= self.HACC_AES_CLR
        if iv is not None:
            piv = bytes_to_dwords(iv)
            self.reg.HACC_ACFG0 = piv[0]
            self.reg.HACC_ACFG1 = piv[1]
            self.reg.HACC_ACFG2 = piv[2]
            self.reg.HACC_ACFG3 = piv[3]
        if encrypt:
            self.reg.HACC_ACON |= self.HACC_AES_ENC
        else:
            self.reg.HACC_ACON &= 0xFFFFFFFE
        pdst = bytearray()
        for pos in range(0, length, 16):
            psrc = bytes_to_dwords(data[(pos % len(data)):(pos % len(data)) + 16])
            plen = len(psrc)
            pos = 0
            for i in range(plen // 4):
                self.reg.HACC_ASRC0 = psrc[pos + 0]
                self.reg.HACC_ASRC1 = psrc[pos + 1]
                self.reg.HACC_ASRC2 = psrc[pos + 2]
                self.reg.HACC_ASRC3 = psrc[pos + 3]
                self.reg.HACC_ACON2 |= self.HACC_AES_START
                i = 0
                while i < 20:
                    if self.reg.HACC_ACON2 & self.HACC_AES_RDY != 0:
                        break
                    i += 1
                if i == 20:
                    self.error("SEJ Hardware seems not to be configured correctly. Results may be wrong.")
                pdst.extend(pack("<I", self.reg.HACC_AOUT0))
                pdst.extend(pack("<I", self.reg.HACC_AOUT1))
                pdst.extend(pack("<I", self.reg.HACC_AOUT2))
                pdst.extend(pack("<I", self.reg.HACC_AOUT3))
        return pdst

    def sej_key_config(self, swkey):
        iv = bytes.fromhex("57325A5A125497661254976657325A5A")
        self.sej_set_mode(AES_CBC_MODE)
        self.sej_set_key(AES_HW_KEY, AES_KEY_128)
        hw_key = self.sej_do_aes(True, iv, swkey, 32)
        self.sej_set_key(AES_HW_WRAP_KEY, AES_KEY_256, hw_key)

    def sej_sec_cfg_sw(self, data, encrypt=True):
        self.sej_set_mode(AES_CBC_MODE)
        self.sej_set_key(AES_SW_KEY, AES_KEY_256, b"1A52A367CB12C458965D32CD874B36B2")
        iv = bytes.fromhex("57325A5A125497661254976657325A5A")
        res = self.sej_do_aes(encrypt, iv, data, len(data))
        return res

    def xor_data(self, data):
        i = 0
        for val in self.g_HACC_CFG_1:
            data[i:i + 4] = pack("<I", unpack("<I", data[i:i + 4])[0] ^ val)
            i += 4
            if i == 16:
                break
        return data

    def sej_sec_cfg_hw(self, data, encrypt=True):
        if encrypt:
            data = self.xor_data(bytearray(data))
        self.info("HACC init")
        self.SEJ_Init(encrypt=encrypt)
        self.info("HACC run")
        dec = self.SEJ_Run(data)
        self.info("HACC terminate")
        self.SEJ_Terminate()
        if not encrypt:
            dec = self.xor_data(dec)
        return dec

    def sej_sec_cfg_hw_V3(self, data, encrypt=True):
        return self.hw_aes128_cbc_encrypt(buf=data, encrypt=encrypt)

    # seclib_get_msg_auth_key
    def generate_rpmb(self, meid, otp, derivedlen=32):
        # self.sej_sec_cfg_decrypt(bytes.fromhex("1FF7EB9EEA3BA346C2C94E3D44850C2172B56BC26D2450CA9ADBAB7136604542C3B2EA50057037669A4C493BF7CC7E6E2644563808F73B3AA5AFE2D48D97597E"))
        # self.sej_key_config(b"1A52A367CB12C458965D32CD874B36B2")
        # self.sej_set_otp(bytes.fromhex("486973656E7365000023232323232323232323230A006420617320302C207468010000009400000040000000797B797B"))
        self.sej_set_otp(otp)
        buf = bytearray()
        meid = bytearray(meid)  # 0x100010
        for i in range(derivedlen):
            buf.append(meid[i % len(meid)])
        return self.hw_aes128_cbc_encrypt(buf=buf, encrypt=True, iv=self.g_HACC_CFG_1)

    def sp_hacc_internal(self, buf: bytes, bAC: bool, user: int, bDoLock: bool, aes_type: int, bEn: bool):
        dec = None
        if user == 0:
            iv = self.g_HACC_CFG_1
            self.info("HACC init")
            self.SEJ_V3_Init(ben=bEn, iv=iv)
            self.info("HACC run")
            dec = self.SEJ_Run(buf)
            self.info("HACC terminate")
            self.SEJ_Terminate()
        elif user == 1:
            iv = self.g_HACC_CFG_2
            self.info("HACC init")
            self.SEJ_V3_Init(ben=bEn, iv=iv)
            self.info("HACC run")
            dec = self.SEJ_Run(buf)
            self.info("HACC terminate")
            self.SEJ_Terminate()
        elif user == 2:
            self.sej_set_key(key=2, flag=32)
            iv = bytes.fromhex("57325A5A125497661254976657325A5A")
            dec = self.sej_do_aes(encrypt=aes_type, iv=iv, data=buf, length=len(buf))
        elif user == 3:
            iv = self.g_HACC_CFG_3
            self.info("HACC init")
            self.SEJ_V3_Init(ben=bEn, iv=iv)
            self.info("HACC run")
            dec = self.SEJ_Run(buf)
            self.info("HACC terminate")
            self.SEJ_Terminate()
        return dec

    def dev_kdf(self, buf: bytes, derivelen=16):
        res = bytearray()
        for i in range(derivelen // 16):
            res.extend(self.sp_hacc_internal(buf=buf[i * 16:(i * 16) + 16], bAC=True, user=0, bDoLock=False, aes_type=1,
                                             bEn=True))
        return res

    def generate_mtee(self, otp=None):
        if otp is not None:
            self.sej_set_otp(otp)
        buf = bytes.fromhex("4B65796D61737465724D617374657200")
        return self.dev_kdf(buf=buf, derivelen=16)

    def generate_mtee_meid(self, meid):
        self.sej_key_config(meid)
        res1 = self.sej_do_aes(True, None, meid, 32)
        return self.sej_do_aes(True, None, res1, 32)

    def generate_mtee_hw(self, otp=None):
        if otp is not None:
            self.sej_set_otp(otp)
        self.info("HACC init")
        self.SEJ_Init_MTEE(encrypt=True)
        self.info("HACC run")
        dec = self.SEJ_Run(bytes.fromhex("7777772E6D6564696174656B2E636F6D30313233343536373839414243444546"))
        self.info("HACC terminate")
        self.SEJ_Terminate()
        return dec
