from struct import unpack, pack
import hashlib


class seccfg:
    def __init__(self, hwc):
        self.hwc = hwc
        self.magic = 0x4D4D4D4D
        self.seccfg_ver = None
        self.seccfg_size = None
        self.lock_state = None
        self.critical_lock_state = None
        self.sboot_runtime = None
        self.endflag = 0x45454545
        self.hash = b""

    def parse(self, data):
        seccfg_data = unpack("<IIIIIII", data[:7 * 4])
        self.magic, self.seccfg_ver, self.seccfg_size, self.lock_state, self.critical_lock_state, \
        self.sboot_runtime, self.endflag = seccfg_data
        self.hash = data[7 * 4:(7 * 4) + 32]
        if self.magic != 0x4D4D4D4D or self.endflag != 0x45454545:
            self.error("Unknown seccfg structure !")
            return False
        return True

        """
        LKS_DEFAULT = 0x01
        LKS_MP_DEFAULT = 0x02
        LKS_UNLOCK = 0x03
        LKS_LOCK = 0x04
        LKS_VERIFIED = 0x05
        LKS_CUSTOM = 0x06
        LKCS_UNLOCK = 0x01
        LKCS_LOCK = 0x02
        SBOOT_RUNTIME_OFF = 0
        SBOOT_RUNTIME_ON  = 1
        """

    def create(self, sc_org, hwtype: str, lockflag: str = "unlock", V3=False):
        if sc_org is None:
            if lockflag == "unlock":
                self.lock_state = 3
                self.critical_lock_state = 1
                self.seccfg_ver = 4
                self.seccfg_size = 0x3C
                self.sboot_runtime = 0
            elif lockflag == "lock":
                self.lock_state = 1
                self.critical_lock_state = 0
                self.seccfg_ver = 4
                self.seccfg_size = 0x3C
                self.sboot_runtime = 0
        else:
            self.lock_state = sc_org.lock_state
            self.critical_lock_state = sc_org.critical_lock_state
            self.seccfg_size = sc_org.seccfg_size
            self.sboot_runtime = sc_org.sboot_runtime
            self.seccfg_ver = sc_org.seccfg_ver
        seccfg_data = pack("<IIIIIII", self.magic, self.seccfg_ver, self.seccfg_size, self.lock_state,
                           self.critical_lock_state, self.sboot_runtime, 0x45454545)
        dec_hash = hashlib.sha256(seccfg_data).digest()
        if hwtype == "sw":
            enc_hash = self.hwc.sej.sej_sec_cfg_sw(dec_hash, True)
        else:
            if not V3:
                enc_hash = self.hwc.sej.sej_sec_cfg_hw(dec_hash, True)
            else:
                enc_hash = self.hwc.sej.sej_sec_cfg_hw_V3(dec_hash, True)
        self.hash = enc_hash
        data = seccfg_data + enc_hash
        data += b"\x00" * (0x200 - len(data))
        return bytearray(data)
