class damodes:
    DEFAULT = 0
    XFLASH = 1


class chipconfig:
    def __init__(self, var1=None, watchdog=None, uart=None, brom_payload_addr=None,
                 da_payload_addr=None, pl_payload_addr=None, cqdma_base=None, sej_base=None, dxcc_base=None,
                 gcpu_base=None, ap_dma_mem=None, name="", description="", dacode=None,
                 meid_addr=None, socid_addr=None, blacklist=(), blacklist_count=None,
                 send_ptr=None, ctrl_buffer=(), cmd_handler=None, brom_register_access=None,
                 damode=damodes.DEFAULT, loader=None, prov_addr=None, misc_lock=None):
        self.var1 = var1
        self.watchdog = watchdog
        self.uart = uart
        self.brom_payload_addr = brom_payload_addr
        self.da_payload_addr = da_payload_addr
        self.pl_payload_addr = pl_payload_addr
        self.cqdma_base = cqdma_base
        self.ap_dma_mem = ap_dma_mem
        self.sej_base = sej_base
        self.dxcc_base = dxcc_base
        self.name = name
        self.description = description
        self.dacode = dacode
        self.blacklist = blacklist
        self.blacklist_count = blacklist_count,
        self.send_ptr = send_ptr,
        self.ctrl_buffer = ctrl_buffer,
        self.cmd_handler = cmd_handler,
        self.brom_register_access = brom_register_access,
        self.meid_addr = meid_addr
        self.socid_addr = socid_addr
        self.prov_addr = prov_addr
        self.gcpu_base = gcpu_base
        self.dacode = dacode
        self.damode = damode
        self.loader = loader
        self.misc_lock = misc_lock

    # Credits to cyrozap and Chaosmaster for some values
    """
    0x0:    chipconfig(var1=0x0,
                       watchdog=0x0,
                       uart=0x0,
                       brom_payload_addr=0x0,
                       da_payload_addr=0x0,
                       cqdma_base=0x0,
                       gcpu_base=0x0,
                       blacklist=[(0x0, 0x0),(0x00105704, 0x0)],
                       dacode=0x0,
                       name=""),

                       Needed fields

                       For hashimoto:
                       cqdma_base,
                       ap_dma_mem,
                       blacklist

                       For kamakiri:
                       var1

                       For amonet:
                       gpu_base
                       blacklist
    """


"""
    0x5700: chipconfig(  # var1
        # watchdog
        # uart
        # brom_payload_addr
        # da_payload_addr
        gcpu_base=0x10016000,
        # sej_base
        # no dxcc
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.DEFAULT,
        # dacode
        name="MT5700"),
    0x6588: chipconfig(  # var1
        watchdog=0x10000000,
        # uart
        # brom_payload_addr
        # da_payload_addr
        # gcpu_base
        # sej_base
        # dxcc_base
        # cqdma_base
        ap_dma_mem=0x11000000 + 0x1A0,
        # blacklist
        damode=damodes.DEFAULT,
        dacode=0x6588,
        name="MT6588"),
"""

hwconfig = {
    0x571: chipconfig(  # var1
        watchdog=0x10007000,
        # uart
        # brom_payload_addr
        # da_payload_addr
        # gcpu_base
        # sej_base
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.DEFAULT,  #
        dacode=0x0571,
        name="MT0571"),
    0x598: chipconfig(  # var1
        watchdog=0x10211000,
        uart=0x11020000,
        brom_payload_addr=0x100A00,  # todo:check
        da_payload_addr=0x201000,  # todo:check
        gcpu_base=0x10224000,
        sej_base=0x1000A000,
        cqdma_base=0x10212c00,
        ap_dma_mem=0x11000000 + 0x1A0,
        # blacklist
        damode=damodes.DEFAULT,
        dacode=0x0598,
        name="ELBRUS/MT0598"),
    0x992: chipconfig(  # var1
        # watchdog
        # uart
        # brom_payload_addr
        # da_payload_addr
        # gcpu_base
        # sej_base
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.XFLASH,
        dacode=0x0992,
        name="MT0992"),
    0x2601: chipconfig(
        var1=0xA,  # Smartwatch, confirmed
        watchdog=0x10007000,
        uart=0x11005000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x2008000,
        pl_payload_addr=0x81E00000,  #
        # no gcpu_base =0x10210000,
        sej_base=0x1000A000,  # hacc
        # no dxcc
        # no cqdma_base
        # no ap_dma_mem
        blacklist=[(0x11141F0C, 0x0), (0x11144BC4, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x11141f4c, 0xba68),
        ctrl_buffer=0x11142BE0,
        cmd_handler=0x0040C5AF,
        brom_register_access=(0x40bd48, 0x40befc),
        meid_addr=0x11142C34,
        dacode=0x2601,
        damode=damodes.DEFAULT,  #
        name="MT2601",
        loader="mt2601_payload.bin"),
    0x3967: chipconfig(  # var1
        # watchdog
        # uart
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40020000,
        # gcpu_base
        # sej_base
        # no dxcc
        # cqdma_base
        # ap_dma_mem
        # blacklist
        dacode=0x3967,
        damode=damodes.DEFAULT,
        name="MT3967"),
    0x6255: chipconfig(  # var1
        # watchdog
        # uart
        # brom_payload_addr
        # da_payload_addr
        # gcpu_base
        sej_base=0x80140000,
        # no dxcc
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.DEFAULT,
        # dacode
        name="MT6255"),
    0x6261: chipconfig(
        var1=0x28,  # Smartwatch, confirmed
        watchdog=0xA0030000,
        uart=0xA0080000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        # no gcpu_base
        sej_base=0xA0110000,
        # no dxcc
        # no cqdma_base
        # no ap_dma_mem
        blacklist=[(0xE003FC83, 0)],
        send_ptr=(0x700044b0, 0x700058EC),
        ctrl_buffer=0x700041A8,
        cmd_handler=0x700061F6,
        damode=damodes.DEFAULT,
        dacode=0x6261,
        name="MT6261",
        loader="mt6261_payload.bin"
    ),
    0x6280: chipconfig(  # var1
        # watchdog
        # uart
        # brom_payload_addr
        # da_payload_addr
        # gcpu_base
        sej_base=0x80080000,
        # no dxcc
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.DEFAULT,
        name="MT6280"
    ),
    0x6516: chipconfig(  # var1
        watchdog=0x10003000,
        uart=0x10023000,
        da_payload_addr=0x201000,  # todo: check
        # gcpu_base
        sej_base=0x1002D000,
        # no dxcc
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.DEFAULT,
        dacode=0x6516,
        name="MT6516"),
    0x633: chipconfig(  # var1
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,  # todo: check
        da_payload_addr=0x201000,
        pl_payload_addr=0x80001000,  #
        gcpu_base=0x1020D000,
        sej_base=0x1000A000,
        # no dxcc
        cqdma_base=0x1020ac00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_P_DMA_I2C_RX_MEM_ADDR
        damode=damodes.XFLASH,
        dacode=0x6570,
        name="MT6570"),
    0x6571: chipconfig(  # var1
        watchdog=0x10007400,
        # uart
        da_payload_addr=0x2009000,
        pl_payload_addr=0x80001000,
        # gcpu_base
        # sej_base
        # no dxcc
        # cqdma_base
        # ap_dma_mem
        # blacklist
        misc_lock=0x1000141C,
        damode=damodes.DEFAULT,  #
        dacode=0x6571,
        name="MT6571"),
    0x6572: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11005000,
        brom_payload_addr=0x10036A0,
        da_payload_addr=0x2008000,
        pl_payload_addr=0x81E00000,  #
        # gcpu_base
        # sej_base
        # no dxcc
        # cqdma_base
        ap_dma_mem=0x11000000 + 0x19C,  # AP_P_DMA_I2C_1_MEM_ADDR
        blacklist=[(0x11141F0C, 0), (0x11144BC4, 0)],
        blacklist_count=0x00000008,
        send_ptr=(0x11141f4c, 0x40ba68), ####
        ctrl_buffer=0x11142BE0,
        cmd_handler=0x40C5AF,
        brom_register_access=(0x40bd48, 0x40befc),
        meid_addr=0x11142C34,
        misc_lock=0x1000141C,
        damode=damodes.DEFAULT,  #
        dacode=0x6572,
        name="MT6572",
        loader="mt6572_payload.bin"),
    0x6573: chipconfig(  # var1
        watchdog=0x70025000,
        # uart
        da_payload_addr=0x90006000,
        pl_payload_addr=0xf1020000,
        # gcpu_base
        sej_base=0x7002A000,
        # no dxcc
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.DEFAULT,
        dacode=0x6573,
        name="MT6573/MT6260"),
    0x6575: chipconfig(  # var1
        watchdog=0xC0000000,
        uart=0xC1009000,
        da_payload_addr=0xc2001000,
        pl_payload_addr=0xc2058000,
        # gcpu_base
        sej_base=0xC101A000,
        # no dxcc
        # cqdma_base
        ap_dma_mem=0xC100119C,
        # blacklist
        damode=damodes.DEFAULT,
        dacode=0x6575,
        name="MT6575/77"),
    0x6577: chipconfig(  # var1
        watchdog=0xC0000000,
        uart=0xC1009000,
        da_payload_addr=0xc2001000,
        pl_payload_addr=0xc2058000,
        # gcpu_base
        sej_base=0xC101A000,
        # no dxcc
        # cqdma_base
        ap_dma_mem=0xC100119C,
        # blacklist
        damode=damodes.DEFAULT,
        dacode=0x6577,
        name="MT6577"),
    0x6580: chipconfig(var1=0xAC,
                       watchdog=0x10007000,
                       uart=0x11005000,
                       brom_payload_addr=0x100A00,
                       da_payload_addr=0x201000,
                       pl_payload_addr=0x80001000,  #
                       # no gcpu_base
                       sej_base=0x1000A000,
                       # dxcc_base
                       cqdma_base=0x1020AC00,
                       ap_dma_mem=0x11000000 + 0x1A0,  # AP_P_DMA_I2C_1_RX_MEM_ADDR
                       blacklist=[(0x102764, 0x0), (0x001071D4, 0x0)],
                       blacklist_count=0x00000008,
                       send_ptr=(0x1027a4, 0xb60c),
                       ctrl_buffer=0x00103060,
                       cmd_handler=0x0000C113,
                       brom_register_access=(0xb8e0, 0xba94),
                       misc_lock=0x10001838,
                       meid_addr=0x1030B4,
                       damode=damodes.DEFAULT,
                       dacode=0x6580,
                       name="MT6580",
                       loader="mt6580_payload.bin"),
    0x6582: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x80001000,  #
        gcpu_base=0x1101B000,
        sej_base=0x1000A000,
        # no dxcc
        # no cqdma_base
        ap_dma_mem=0x11000000 + 0x320,  # AP_DMA_I2C_0_RX_MEM_ADDR
        blacklist=[(0x102788, 0x0), (0x00105BE4, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027c8, 0xa5fc),
        ctrl_buffer=0x00103078,
        cmd_handler=0x0000B2E7,
        brom_register_access=(0xa8d0, 0xaa84),
        meid_addr=0x1030CC,
        misc_lock=0x10002050,
        damode=damodes.DEFAULT,  #
        dacode=0x6582,
        name="MT6582/MT6574",
        loader="mt6582_payload.bin"),
    0x6583: chipconfig(  # var1
        watchdog=0x10000000,  # fixme
        uart=0x11006000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x12001000,
        pl_payload_addr=0x80001000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000A000,
        # no dxcc
        # blacklist
        cqdma_base=0x10212000,  # This chip might not support cqdma
        ap_dma_mem=0x11000000 + 0x320,  # AP_DMA_I2C_0_RX_MEM_ADDR
        misc_lock=0x10002050,
        damode=damodes.DEFAULT,
        dacode=0x6589,
        name="MT6583/6589"),
    0x6592: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x111000,
        pl_payload_addr=0x80001000,
        gcpu_base=0x10210000,
        sej_base=0x1000A000,
        # no dxcc
        cqdma_base=0x10212000,  # This chip might not support cqdma
        ap_dma_mem=0x11000000 + 0x320,  # AP_DMA_I2C_0_RX_MEM_ADDR
        blacklist=[(0x00102764, 0), (0x00105BF0, 0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027a4, 0xa564),
        ctrl_buffer=0x00103054,
        cmd_handler=0x0000B09F,
        brom_register_access=(0xa838, 0xa9ec),
        meid_addr=0x1030A8,
        misc_lock=0x10002050,
        dacode=0x6592,
        damode=damodes.DEFAULT,  #
        name="MT6592",
        loader="mt6592_payload.bin"),
    0x6595: chipconfig(var1=0xA,
                       watchdog=0x10007000,
                       uart=0x11002000,
                       brom_payload_addr=0x100A00,
                       da_payload_addr=0x111000,
                       # gcpu_base
                       sej_base=0x1000A000,
                       # dxcc_base
                       # cqdma_base
                       ap_dma_mem=0x11000000 + 0x1A0,
                       blacklist=[(0x00102768, 0), (0x0106c88, 0)],
                       blacklist_count=0x00000008,
                       send_ptr=(0x1027a8, 0xb218),
                       ctrl_buffer=0x00103050,
                       cmd_handler=0x0000BD53,
                       brom_register_access=(0xb4ec, 0xb6a0),
                       meid_addr=0x1030A4,
                       dacode=0x6595,
                       damode=damodes.DEFAULT,  #
                       name="MT6595",
                       loader="mt6595_payload.bin"),
    # 6725
    0x321: chipconfig(
        var1=0x28,
        watchdog=0x10212000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10216000,
        sej_base=0x10008000,  # hacc
        # no dxcc
        cqdma_base=0x10217C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_O_RX_MEM_ADDR
        blacklist=[(0x00102760, 0x0), (0x00105704, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027a0, 0x95f8),
        ctrl_buffer=0x0010305C,
        cmd_handler=0x0000A17F,
        brom_register_access=(0x98cc, 0x9a94),
        meid_addr=0x1030B0,
        misc_lock=0x10001838,
        damode=damodes.DEFAULT,  #
        dacode=0x6735,
        name="MT6735/T",
        loader="mt6735_payload.bin"),
    0x335: chipconfig(
        var1=0x28,  # confirmed
        watchdog=0x10212000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10216000,
        sej_base=0x10008000,
        # no dxcc
        cqdma_base=0x10217C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_O_RX_MEM_ADDR
        blacklist=[(0x00102760, 0x0), (0x00105704, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027a0, 0x9608),
        ctrl_buffer=0x0010305C,
        cmd_handler=0x0000A18F,
        brom_register_access=(0x98dc, 0x9aa4),
        meid_addr=0x1030B0,
        damode=damodes.DEFAULT,  #
        dacode=0x6735,
        name="MT6737M",
        loader="mt6737_payload.bin"),
    # MT6738
    0x699: chipconfig(
        var1=0xB4,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000,
        sej_base=0x1000A000,  # hacc
        dxcc_base=0x10210000,
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000000 + 0x1a0,  # AP_DMA_I2C_1_RX_MEM_ADDR
        blacklist=[(0x10282C, 0x0), (0x001076AC, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x102870, 0xdf1c),
        ctrl_buffer=0x00102A28,
        cmd_handler=0x0000EC49,
        brom_register_access=(0xe330, 0xe3e8),
        meid_addr=0x102AF8,
        socid_addr=0x102b08,
        prov_addr=0x10720C,
        misc_lock=0x1001a100,
        damode=damodes.XFLASH,
        dacode=0x6739,
        name="MT6739/MT6731",
        loader="mt6739_payload.bin"),
    0x601: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000A000,  # hacc
        cqdma_base=0x10212C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_1_RX_MEM_ADDR
        # blacklist
        misc_lock=0x10001838,
        damode=damodes.XFLASH,
        dacode=0x6755,
        name="MT6750"),
    0x6752: chipconfig(  # var1
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,  #
        pl_payload_addr=0x40001000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000A000,  # hacc
        # no dxcc
        cqdma_base=0x10212C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_0_RX_MEM_ADDR
        # blacklist
        damode=damodes.DEFAULT,  #
        dacode=0x6752,
        name="MT6752"),
    0x337: chipconfig(
        var1=0x28,  # confirmed
        watchdog=0x10212000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10216000,
        sej_base=0x10008000,
        # no dxcc
        cqdma_base=0x10217C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_0_RX_MEM_ADDR
        blacklist=[(0x00102760, 0x0), (0x00105704, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027a0, 0x9668),
        ctrl_buffer=0x0010305C,
        cmd_handler=0x0000A1EF,
        brom_register_access=(0x993c, 0x9b04),
        meid_addr=0x1030B0,
        damode=damodes.DEFAULT,  #
        dacode=0x6735,
        misc_lock=0x10001838,
        name="MT6753",
        loader="mt6753_payload.bin"),
    0x326: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000A000,  # hacc
        # no dxcc
        cqdma_base=0x10212C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_1_RX_MEM_ADDR
        blacklist=[(0x10276C, 0x0), (0x00105704, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027b0, 0x9a6c),
        ctrl_buffer=0x00103058,
        cmd_handler=0x0000A5FF,
        brom_register_access=(0x9d4c, 0x9f14),
        meid_addr=0x1030AC,
        damode=damodes.XFLASH,
        dacode=0x6755,
        name="MT6755/MT6750/M/T/S",
        description="Helio P10/P15/P18",
        loader="mt6755_payload.bin"),
    0x551: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000A000,
        # no dxcc
        cqdma_base=0x10212C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_1_RX_MEM_ADDR
        blacklist=[(0x102774, 0x0), (0x00105704, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x1027b8, 0x9c2c),
        ctrl_buffer=0x00103060,
        cmd_handler=0x0000A8FB,
        brom_register_access=(0xa030, 0xa0e8),
        meid_addr=0x1030B4,
        misc_lock=0x10001838,
        damode=damodes.XFLASH,
        dacode=0x6757,
        name="MT6757/MT6757D",
        description="Helio P20",
        loader="mt6757_payload.bin"),
    0x688: chipconfig(
        var1=0xA,
        watchdog=0x10211000, #
        uart=0x11020000,
        brom_payload_addr=0x100A00, #
        da_payload_addr=0x201000, #
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000, #
        sej_base=0x10080000,  # hacc
        dxcc_base=0x11240000, #
        cqdma_base=0x10200000, #
        ap_dma_mem=0x11000000 + 0x1A0, #
        blacklist=[(0x102830,0),(0x106A60,0)],
        blacklist_count=0xA,
        send_ptr=(0x102874,0xd860),
        ctrl_buffer=0x102B28,
        cmd_handler=0xE58D, 
        brom_register_access=(0xdc74,0xdd2c),
        meid_addr=0x102bf8,
        socid_addr=0x102c08,
        damode=damodes.XFLASH,
        dacode=0x6758,
        name="MT6758",
        description="Helio P30",
        loader="mt6758_payload.bin"
    ),
    0x507: chipconfig(  # var1
        watchdog=0x10210000,
        uart=0x11020000,
        brom_payload_addr=0x100A00,  # todo
        da_payload_addr=0x201000,
        # pl_payload_addr
        gcpu_base=0x10210000,
        # sej_base
        # dxcc_base
        # cqdma_base
        ap_dma_mem=0x1030000 + 0x1A0,  # todo
        # blacklist
        # blacklist_count
        # send_ptr
        # ctrl_buffer
        # cmd_handler
        # brom_Register_access
        # meid_addr
        damode=damodes.DEFAULT,
        dacode=0x6758,
        name="MT6759",
        description="Helio P30"
        # loader
    ),

    0x717: chipconfig(
        var1=0x25,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000,
        sej_base=0x1000A000,  # hacc
        dxcc_base=0x10210000,
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000a80 + 0x1a0,  # AP_DMA_I2C_CH0_RX_MEM_ADDR
        blacklist=[(0x102828, 0x0), (0x00105994, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x10286c, 0xbc8c),
        ctrl_buffer=0x00102A28,
        cmd_handler=0x0000C9B9,
        brom_register_access=(0xc0a0, 0xc158),
        meid_addr=0x102AF8,
        socid_addr=0x102b08,
        prov_addr=0x1054F4,
        misc_lock=0x1001a100,
        damode=damodes.XFLASH,
        dacode=0x6761,
        name="MT6761/MT6762/MT3369/MT8766B",
        description="Helio A20/P22/A22/A25/G25",
        loader="mt6761_payload.bin"),
    0x690: chipconfig(
        var1=0x7F,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000,
        dxcc_base=0x10210000,
        sej_base=0x1000A000,  # hacc
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000a80 + 0x1a0,
        blacklist=[(0x102834, 0x0), (0x00106CA4, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x102878, 0xd66c),
        ctrl_buffer=0x00102A90,
        cmd_handler=0x0000E383,
        brom_register_access=(0xda80, 0xdb38),
        meid_addr=0x102B78,
        socid_addr=0x102b88,
        prov_addr=0x106804,
        misc_lock=0x1001a100,
        damode=damodes.XFLASH,
        dacode=0x6763,
        name="MT6763",
        description="Helio P23",
        loader="mt6763_payload.bin"),
    0x766: chipconfig(
        var1=0x25,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000,  # not confirmed
        sej_base=0x1000a000,  # hacc
        dxcc_base=0x10210000,
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000000 + 0x1a0,  # AP_DMA_I2C2_CH0_RX_MEM_ADDR
        blacklist=[(0x102828, 0x0), (0x00105994, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x10286c, 0xbdc0),
        ctrl_buffer=0x00102A28,
        cmd_handler=0x0000CAED,
        brom_register_access=(0xc1d4, 0xc28c),
        meid_addr=0x102AF8,
        socid_addr=0x102b08,
        prov_addr=0x1054F4,
        misc_lock=0x1001a100,
        damode=damodes.XFLASH,
        dacode=0x6765,
        name="MT6765/MT8768t",
        description="Helio P35/G35",
        loader="mt6765_payload.bin"),
    0x707: chipconfig(
        var1=0x25,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000,
        sej_base=0x1000A000,  # hacc
        dxcc_base=0x10210000,
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000000 + 0x1A0,
        blacklist=[(0x10282C, 0x0), (0x00105994, 0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x10286c, 0xc190),
        ctrl_buffer=0x00102A28,
        cmd_handler=0x0000CF15,
        brom_register_access=(0xc598, 0xc650),
        meid_addr=0x102AF8,
        socid_addr=0x102b08,
        prov_addr=0x1054F4,
        misc_lock=0x1001a100,
        damode=damodes.XFLASH,
        dacode=0x6768,
        name="MT6768",
        description="Helio P65/G85 k68v1",
        loader="mt6768_payload.bin"),
    0x788: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000,
        sej_base=0x1000A000,  # hacc
        dxcc_base=0x10210000,  # dxcc_sec
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000000 + 0x158,  # AP_DMA_I2C_1_RX_MEM_ADDR
        blacklist=[(0x00102834, 0x0), (0x00106A60, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x102878, 0xdebc),
        ctrl_buffer=0x00102A80,
        cmd_handler=0x0000EBE9,
        brom_register_access=(0xe2d0, 0xe388),
        meid_addr=0x102B38,
        socid_addr=0x102B48,
        prov_addr=0x1065C0,
        misc_lock=0x1001a100,
        damode=damodes.XFLASH,
        dacode=0x6771,
        name="MT6771/MT8385/MT8183/MT8666",
        description="Helio P60/P70/G80",
        loader="mt6771_payload.bin"),
    # blacklist=[(0x00102830, 0x00200008),  # Static permission table pointer
    #           (0x00102834, 2),  # Static permission table entry count
    #           (0x00200000, 0x00000000),  # Memory region minimum address
    #           (0x00200004, 0xfffffffc),  # Memory region maximum address
    #           (0x00200008, 0x00000200),  # Memory read command bitmask
    #           (0x0020000c, 0x00200000),  # Memory region array pointer
    #           (0x00200010, 0x00000001),  # Memory region array length
    #           (0x00200014, 0x00000400),  # Memory write command bitmask
    #           (0x00200018, 0x00200000),  # Memory region array pointer
    #           (0x0020001c, 0x00000001),  # Memory region array length
    #           (0x00106A60, 0)],  # Dynamic permission table entry count?),
    0x725: chipconfig(var1=0xA,  # confirmed
                      watchdog=0x10007000,
                      uart=0x11002000,
                      brom_payload_addr=0x100A00,
                      da_payload_addr=0x201000,
                      pl_payload_addr=0x40200000,  #
                      gcpu_base=0x10050000,
                      sej_base=0x1000a000,  # hacc
                      dxcc_base=0x10210000,
                      cqdma_base=0x10212000,
                      ap_dma_mem=0x11000000 + 0x158,
                      blacklist=[(0x102838, 0x0), (0x00106A60, 0x0)],
                      blacklist_count=0x0000000A,
                      send_ptr=(0x102878, 0xe04c),
                      ctrl_buffer=0x00102A80,
                      cmd_handler=0x0000ED6D,
                      brom_register_access=(0xe454, 0xe50c),
                      meid_addr=0x102B38,
                      socid_addr=0x102B48,
                      prov_addr=0x1065C0,
                      misc_lock=0x1001a100,
                      damode=damodes.XFLASH,
                      dacode=0x6779,
                      name="MT6779",
                      description="Helio P90 k79v1",
                      loader="mt6779_payload.bin"),
    0x1066: chipconfig(
        var1=0x73, #confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,
        gcpu_base=0x10050000,
        sej_base=0x1000A000,  # hacc
        dxcc_base=0x10210000,
        # cqdma_base=0x10212000,
        # ap_dma_mem=0x11000000 + 0x158,
        blacklist=[(0x10284C, 0x106B54)],
        blacklist_count=0x0000000A,
        send_ptr=(0x102890,0xe5d8),
        ctrl_buffer=0x00102AB4,
        cmd_handler=0x0000F3C1,
        brom_register_access=(0xe9dc,0xea94),
        meid_addr=0x102B98,
        socid_addr=0x102BA8,
        damode=damodes.XFLASH,
        dacode=0x6781,
        name="MT6781",
        description="Helio G96",
        loader="mt6781_payload.bin"
    ),
    0x813: chipconfig(var1=0xA,  # confirmed
                      watchdog=0x10007000,
                      uart=0x11002000,
                      brom_payload_addr=0x100A00,
                      da_payload_addr=0x201000,
                      pl_payload_addr=0x40200000,  #
                      gcpu_base=0x10050000,
                      sej_base=0x1000A000,  # hacc
                      dxcc_base=0x10210000,
                      cqdma_base=0x10212000,
                      ap_dma_mem=0x11000000 + 0x158,
                      blacklist=[(0x102838, 0x0), (0x00106A60, 0x0)],
                      blacklist_count=0x0000000A,
                      send_ptr=(0x102878, 0xe2a4),
                      ctrl_buffer=0x00102A80,
                      cmd_handler=0x0000F029,
                      brom_register_access=(0xe6ac, 0xe764),
                      meid_addr=0x102B38,
                      socid_addr=0x102B48,
                      prov_addr=0x1065C0,
                      misc_lock=0x1001a100,
                      damode=damodes.XFLASH,
                      dacode=0x6785,
                      name="MT6785",
                      description="Helio G90",
                      loader="mt6785_payload.bin"),
    0x6795: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x110000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000A000,  # hacc
        # no dxcc
        cqdma_base=0x10212c00,
        ap_dma_mem=0x11000000 + 0x1A0,
        blacklist=[(0x102764, 0x0), (0x00105704, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027a4, 0x978c),
        ctrl_buffer=0x0010304C,
        cmd_handler=0x0000A313, #
        brom_register_access=(0x9a60, 0x9c28),
        meid_addr=0x1030A0,
        damode=damodes.DEFAULT,  #
        dacode=0x6795,
        name="MT6795",
        description="Helio X10",
        loader="mt6795_payload.bin"),
    0x279: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10210000,
        # no dxcc
        sej_base=0x1000A000,  # hacc
        cqdma_base=0x10212C00,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_1_RX_MEM_ADDR
        blacklist=[(0x0010276C, 0x0), (0x00105704, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1027b0, 0x9eac),
        ctrl_buffer=0x00103058,
        cmd_handler=0x0000AA3F,
        brom_register_access=(0xa18c, 0xa354),
        meid_addr=0x1030AC,
        misc_lock=0x10002050,
        damode=damodes.XFLASH,
        dacode=0x6797,
        name="MT6797/MT6767",
        description="Helio X23/X25/X27",
        loader="mt6797_payload.bin"),
    0x562: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10211000,
        uart=0x11020000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,  # not confirmed
        gcpu_base=0x10210000,
        cqdma_base=0x11B30000,
        ap_dma_mem=0x11000000 + 0x1A0,  # AP_DMA_I2C_2_RX_MEM_ADDR
        dxcc_base=0x11B20000,
        sej_base=0x1000A000,
        blacklist=[(0x00102870, 0x0), (0x00107070, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x1028b4, 0xf5ac),
        ctrl_buffer=0x001032F0,
        cmd_handler=0x000102C3,
        brom_register_access=(0xf9c0, 0xfa78),
        meid_addr=0x1033B8,
        socid_addr=0x1033C8,
        damode=damodes.XFLASH,
        dacode=0x6799,
        name="MT6799",
        description="Helio X30/X35",
        loader="mt6799_payload.bin"),
    0x989: chipconfig(
        var1=0x73,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,  #
        da_payload_addr=0x201000,  #
        pl_payload_addr=0x40200000,  #
        gcpu_base=0x10050000,
        dxcc_base=0x10210000,
        sej_base=0x1000a000,  # hacc
        cqdma_base=0x10212000,
        ap_dma_mem=0x10217a80 + 0x1a0,
        blacklist=[(0x00102844, 0x0), (0x00106B54, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x102884, 0xdfe0),
        ctrl_buffer=0x00102AA4,
        cmd_handler=0x0000EDAD,
        brom_register_access=(0xe3e8, 0xe4a0),
        meid_addr=0x102b98,
        socid_addr=0x102ba8,
        prov_addr=0x1066B4,
        damode=damodes.XFLASH,
        dacode=0x6833,
        name="MT6833",
        description="Dimensity 700 5G k6833",
        loader="mt6833_payload.bin"),
    0x996: chipconfig(var1=0xA,
                      watchdog=0x10007000,
                      uart=0x11002000,
                      brom_payload_addr=0x100A00,
                      da_payload_addr=0x201000,
                      pl_payload_addr=0x40200000,  #
                      gcpu_base=0x10050000,
                      dxcc_base=0x10210000,
                      cqdma_base=0x10212000,
                      sej_base=0x1000a000,  # hacc
                      ap_dma_mem=0x10217a80 + 0x1A0,
                      blacklist=[(0x10284C, 0x0), (0x00106B60, 0x0)],
                      blacklist_count=0x0000000A,
                      send_ptr=(0x10288c, 0xea64),
                      ctrl_buffer=0x00102AA0,
                      cmd_handler=0x0000F831,
                      brom_register_access=(0xee6c, 0xef24),
                      meid_addr=0x102b78,
                      socid_addr=0x102b88,
                      prov_addr=0x1066C0,
                      misc_lock=0x1001A100,
                      damode=damodes.XFLASH,
                      dacode=0x6853,
                      name="MT6853",
                      description="Dimensity 720 5G",
                      loader="mt6853_payload.bin"),
    0x886: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,
        gcpu_base=0x10050000,
        dxcc_base=0x10210000,
        sej_base=0x1000a000,  # hacc
        cqdma_base=0x10212000,
        ap_dma_mem=0x10217a80 + 0x1A0,
        blacklist=[(0x10284C, 0x0), (0x00106B60, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x10288c, 0xea78),
        ctrl_buffer=0x00102AA0,
        cmd_handler=0x0000F7FD,
        brom_register_access=(0xee80, 0xef38),
        meid_addr=0x102B78,
        socid_addr=0x102B88,
        prov_addr=0x1066C0,
        misc_lock=0x1001A100,
        damode=damodes.XFLASH,
        dacode=0x6873,
        name="MT6873",
        description="Dimensity 800/820 5G",
        loader="mt6873_payload.bin"),
    0x959: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,
        gcpu_base=0x10050000,
        sej_base=0x1000a000,  # hacc
        dxcc_base=0x10210000,
        cqdma_base=0x10212000,
        ap_dma_mem=0x10217a80 + 0x1A0,
        blacklist=[(0x102848, 0x0), (0x00106B60, 0x0)],
        blacklist_count=0xA,
        send_ptr=(0x102888,0xe8d0),
        ctrl_buffer=0x00102A9C,
        cmd_handler=0x0000F69D,
        brom_register_access=(0xecd8,0xed90),
        meid_addr=0x102b98,
        socid_addr=0x102ba8,
        prov_addr=0x1066C0,
        damode=damodes.XFLASH,
        dacode=0x6877,  # todo
        name="MT6877",
        description="Dimensity 900",
        loader="mt6877_payload.bin"
    ),
    0x816: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,
        gcpu_base=0x10050000,
        dxcc_base=0x10210000,
        sej_base=0x1000a000,  # hacc
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000a80 + 0x1a0,
        blacklist=[(0x102848, 0x0), (0x00106B60, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x102888, 0xE6FC),
        ctrl_buffer=0x00102A9C,
        cmd_handler=0x0000F481,
        brom_register_access=(0xeb04, 0xebbc),
        meid_addr=0x102B78,
        socid_addr=0x102B88,
        prov_addr=0x1066C0,
        misc_lock=0x1001A100,
        damode=damodes.XFLASH,
        dacode=0x6885,
        name="MT6885/MT6883/MT6889/MT6880/MT6890",
        description="Dimensity 1000L/1000",
        loader="mt6885_payload.bin"),
    0x950: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,
        gcpu_base=0x10050000,
        dxcc_base=0x10210000,
        sej_base=0x1000a000,  # hacc
        cqdma_base=0x10212000,
        ap_dma_mem=0x11000a80 + 0x1a0,
        blacklist=[(0x102848, 0x0), (0x00106B60, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x102888, 0xE79C),
        ctrl_buffer=0x00102A9C,
        cmd_handler=0x0000F569,
        brom_register_access=(0xeba4, 0xec5c),
        meid_addr=0x102B98,
        socid_addr=0x102BA8,
        prov_addr=0x1066C0,
        damode=damodes.XFLASH,
        dacode=0x6893,
        name="MT6893",
        description="Dimensity 1200",
        loader="mt6893_payload.bin"),
    # Dimensity 1100 - MT6891 Realme Q3 Pro
    0x8110: chipconfig(  # var1
        # watchdog
        # uart
        # brom_payload_addr
        # da_payload_addr
        # gcpu_base
        # sej_base
        # cqdma_base
        # ap_dma_mem
        # blacklist
        damode=damodes.XFLASH,
        dacode=0x8110,
        name="MT8110"),
    0x8127: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x80001000,
        gcpu_base=0x11010000,
        sej_base=0x1000A000,
        # no cqdma_base
        ap_dma_mem=0x11000000 + 0x1A0,
        blacklist=[(0x102870, 0x0), (0x00106C7C, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1028b0, 0xb2b8),
        ctrl_buffer=0x00103178,
        cmd_handler=0x0000BDF3,
        brom_register_access=(0xb58c, 0xb740),
        meid_addr=0x1031CC,
        misc_lock=0x10002050,
        damode=damodes.DEFAULT,  #
        dacode=0x8127,
        name="MT8127/MT3367",
        loader="mt8127_payload.bin"),  # ford,austin,tank #mhmm wdt, nochmal checken
    0x8135: chipconfig(  # var1
        watchdog=0x10000000,
        # uart
        # brom_payload_addr
        da_payload_addr=0x12001000,
        # pl_payload_addr
        # gcpu_base
        # sej_base
        # cqdma_base
        # ap_dma_mem
        # blacklist
        # blacklist_count
        # send_ptr
        # ctrl_buffer
        # cmd_handler
        # brom_register_access
        # meid_addr
        # socid_addr
        damode=damodes.DEFAULT,  #
        dacode=0x8135,
        name="MT8135"
        # description
        # loader
    ),
    0x8163: chipconfig(
        var1=0xB1,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40001000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000A000,
        # no dxcc
        cqdma_base=0x10212C00,
        ap_dma_mem=0x11000000 + 0x1A0,
        blacklist=[(0x102868, 0x0), (0x001072DC, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1028a8, 0xc12c),
        ctrl_buffer=0x0010316C,
        cmd_handler=0x0000CCB3,
        brom_register_access=(0xc400, 0xc5c8),
        meid_addr=0x1031C0,
        misc_lock=0x10002050,
        damode=damodes.DEFAULT,  #
        dacode=0x8163,
        name="MT8163",
        loader="mt8163_payload.bin"),  # douglas, karnak
    0x8167: chipconfig(var1=0xCC,
                       watchdog=0x10007000,
                       uart=0x11005000,
                       brom_payload_addr=0x100A00,
                       da_payload_addr=0x201000,
                       pl_payload_addr=0x40001000,  #
                       gcpu_base=0x1020D000,
                       sej_base=0x1000A000,
                       # no dxcc
                       cqdma_base=0x10212C00,
                       ap_dma_mem=0x11000000 + 0x1A0,
                       blacklist=[(0x102968, 0x0), (0x00107954, 0x0)],
                       blacklist_count=0x0000000A,
                       send_ptr=(0x1029ac, 0xd2e4),
                       ctrl_buffer=0x0010339C,
                       cmd_handler=0x0000DFF7,
                       brom_register_access=(0xd6f2, 0xd7ac),
                       meid_addr=0x103478,
                       socid_addr=0x103488,
                       damode=damodes.XFLASH,
                       dacode=0x8167,
                       name="MT8167/MT8516/MT8362",
                       # description
                       loader="mt8167_payload.bin"),
    0x8168: chipconfig(  # var1
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        # pl_payload_addr=0x40001000
        # gcpu_base
        # sej_base=0x1000A000,
        # cqdma_base
        ap_dma_mem=0x11000280 + 0x1A0,
        # blacklist
        # blacklist_count
        # send_ptr
        # ctrl_buffer
        # cmd_handler
        # brom_register_access
        # meid_addr
        # socid_addr
        damode=damodes.XFLASH,
        dacode=0x8168,
        name="MT8168"
        # description
        # loader
    ),
    0x8172: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x120A00,
        da_payload_addr=0xC0000,
        pl_payload_addr=0x40001000,  #
        gcpu_base=0x10210000,
        sej_base=0x1000a000,
        # no dxcc
        cqdma_base=0x10212c00,
        ap_dma_mem=0x11000000 + 0x1A0,
        blacklist=[(0x122774, 0x0), (0x00125904, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1227b4, 0xa0e4),
        ctrl_buffer=0x0012305C,
        cmd_handler=0x0000AC6B,
        brom_register_access=(0xa3b8, 0xa580),
        meid_addr=0x1230B0,
        misc_lock=0x1202050,
        damode=damodes.DEFAULT,  #
        dacode=0x8173,
        name="MT8173",
        # description
        loader="mt8173_payload.bin"),  # sloane, suez
    0x8176: chipconfig(
        # var1
        watchdog=0x10212c00,
        uart=0x11002000,
        brom_payload_addr=0x120A00,
        da_payload_addr=0xC0000,
        pl_payload_addr=0x40200000,
        gcpu_base=0x10210000,
        sej_base=0x1000A000,
        # no dxcc
        cqdma_base=0x10212c00,
        ap_dma_mem=0x11000000 + 0x1A0,
        # blacklist
        # blacklist_count
        # send_ptr
        # ctrl_buffer
        # cmd_handler
        # brom_register_access
        # meid_addr
        # socid_addr
        dacode=0x8173,
        damode=damodes.DEFAULT,
        # description
        name="MT8176"
        # loader
    ),
    0x930: chipconfig(
        # var1
        watchdog=0x10007000,
        uart=0x11001200,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40200000,
        # gcpu_base
        # sej_base
        # cqdma_base
        # ap_dma_mem
        # blacklist
        # blacklist_count
        # send_ptr
        # ctrl_buffer
        # cmd_handler
        # brom_register_access
        # meid_addr
        # socid_addr
        misc_lock=0x1001A100,
        dacode=0x8195,
        damode=damodes.XFLASH,
        # description
        name="MT8195"
        # loader
    ),
    0x8512: chipconfig(
        var1=0xA,
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x111000,
        pl_payload_addr=0x40200000,
        gcpu_base=0x1020F000,
        sej_base=0x1000A000,
        cqdma_base=0x10214000,
        ap_dma_mem=0x11000000 + 0x1A0,
        blacklist=[(0x001041E4, 0x0), (0x0010AA84, 0x0)],
        blacklist_count=0xA,
        send_ptr=(0x104258, 0xcc44),
        ctrl_buffer=0x00104570,
        cmd_handler=0x0000D7AB,
        brom_register_access=(0xd034, 0xd194),
        meid_addr=0x104638,
        socid_addr=0x104648,
        dacode=0x8512,
        damode=damodes.XFLASH,
        # description
        name="MT8512",
        loader="mt8512_payload.bin"
    ),
    0x8518: chipconfig(  # var1
        # watchdog
        # uart
        # brom_payload_addr
        # da_payload_addr
        # gcpu_base
        # sej_base
        # cqdma_base
        # ap_dma_mem
        # blacklist
        # blacklist_count
        # send_ptr
        # ctrl_buffer
        # cmd_handler
        # brom_register_access
        # meid_addr
        # socid_addr
        dacode=0x8518,
        damode=damodes.XFLASH,
        name="MT8518"
        # loader
    ),
    0x8590: chipconfig(
        var1=0xA,  # confirmed, router
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x80001000,
        gcpu_base=0x1101B000,
        sej_base=0x1000A000,
        # cqdma_base
        # ap_dma_mem=0x11000000 + 0x1A0,
        blacklist=[(0x102870, 0x0), (0x106c7c, 0x0)],
        blacklist_count=0x00000008,
        send_ptr=(0x1028b0, 0xbbe4),
        ctrl_buffer=0x00103184,
        cmd_handler=0x0000C71F,
        brom_register_access=(0xbeb8, 0xc06c),
        meid_addr=0x1031D8,
        dacode=0x8590,
        damode=damodes.DEFAULT,
        name="MT8590/MT7683/MT8521/MT7623",
        # description=
        loader="mt8590_payload.bin"),
    0x8695: chipconfig(
        var1=0xA,  # confirmed
        watchdog=0x10007000,
        uart=0x11002000,
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        pl_payload_addr=0x40001000,  #
        # gcpu_base
        sej_base=0x1000A000,
        # cqdma_base
        ap_dma_mem=0x11000280 + 0x1A0,
        blacklist=[(0x103048, 0x0), (0x00106EC4, 0x0)],
        blacklist_count=0x0000000A,
        send_ptr=(0x103088, 0xbeec),
        ctrl_buffer=0x001031EC,
        cmd_handler=0x0000CAA7,
        brom_register_access=(0xc298, 0xc3f8),
        meid_addr=0x1032B8,
        damode=damodes.XFLASH,
        dacode=0x8695,
        name="MT8695",  # mantis
        # description
        loader="mt8695_payload.bin"),
    0x908: chipconfig(
        # var1
        watchdog=0x10007000,
        # uart
        brom_payload_addr=0x100A00,
        da_payload_addr=0x201000,
        # gcpu_base
        # sej_base
        # cqdma_base
        # ap_dma_mem
        # blacklist
        # blacklist_count
        # send_ptr
        # ctrl_buffer
        # cmd_handler
        # brom_register_access
        # meid_addr
        # socid_addr
        damode=damodes.XFLASH,
        dacode=0x8696,
        # description
        name="MT8696"
        # loader
    ),
}


