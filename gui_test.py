import sys
import time
import mtk
import mock
import logging
import traceback
from mtkclient.Library.mtk_da_cmd import DA_handler
import os

'''guid_gpt = gpt(
            num_part_entries=gpt_settings.gpt_num_part_entries,
            part_entry_size=gpt_settings.gpt_part_entry_size,
            part_entry_start_lba=gpt_settings.gpt_part_entry_start_lba,
        )'''
variables = mock.Mock()
#variables.cmd = "stage"
print(mtk.gpt_settings(0,0,0));
variables.gpt_settings = mtk.gpt_settings(0,0,0)
variables.debugmode = True

loglevel = logging.INFO
config = mtk.Mtk_Config(loglevel=loglevel)
config.gpt_settings = mtk.gpt_settings(0,0,0)  #This actually sets the right GPT settings..
MtkTool = mtk.Main(variables)
mtkClass = mtk.Mtk(config=config, loglevel=loglevel)
print(mtkClass.config.gpt_settings)
#mtkClass.daloader.reinit();
if mtkClass.preloader.init():
    print("connected!")

# Init DA / FLash here
da_handler = DA_handler(mtkClass, loglevel)
res = da_handler.configure_da(mtkClass, preloader=None)
# res = DA was loaded correctly

def dumpPartDone():
    print("dump klaar!")
if not res:
    # Start commands here
    print(mtkClass.config.gpt_settings)
    guid_gpt = None
    #data, guid_gpt = mtkClass.daloader.get_gpt()
    if guid_gpt is None:
        print("Error reading gpt")
    else:
        guid_gpt.print()

    variables = mock.Mock()
    variables.partitionname = "recovery"
    variables.filename = os.path.join("c:\\temp\\", variables.partitionname + ".bin")
    variables.parttype = None
    da_handler.close = dumpPartDone  # Ignore the normally used sys.exit
    da_handler.handle_da_cmds(mtkClass, "r", variables)
else:
    print(res)
mtkClass.port.close();