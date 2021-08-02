# mtkclient
Just some mtk tool for exploitation, reading/writing flash and doing crazy stuff. For linux, a patched kernel is only needed for kamakiri (see Setup folder) (except for read/write flash).
For windows, you need to install zadig driver and replace pid 0003 / pid 2000 driver with WinUSB one (not ! libusb0/libusbK).

Once the mtk script is running, boot into brom mode by powering off device, press and hold either
vol up + power or vol down + power and connect the phone. Once detected by the tool,
release the buttons.

## Credits
- kamakiri [xyzz]
- kamakiri2 (to be renamed) [most likely pandora, need to be confirmed]
- Chaosmaster
- All contributors

## Installation

### Use Re LiveDVD (everything ready to go):
[Download Re Live DVD](https://drive.google.com/file/d/1aroCr2VaXON6fWB6G8R1sz8wMvSbleck/view?usp=sharing)
User: livedvd, Password:livedvd

### Use FireISO as LiveDVD:
[Download FireIso Live DVD](https://github.com/amonet-kamakiri/fireiso/releases/tag/v2.0.0)


## Install

### Linux

#### Install python >=3.8, git and other deps

```
sudo apt install python3 git libusb1.0
```

#### Grab files 
```
git clone https://github.com/bkerler/mtkclient
cd mtkclient
pip3 install -r requirements.txt
python3 setup.py build
python3 setup.py install
```

#### Install rules
```
sudo adduser $USER dialout
sudo adduser $USER plugdev
sudo cp Setup/Linux/*.rules /etc/udev/rules.d
sudo udevadm control -R
```

#### Use kamakiri (optional, only needed for mt6260 or older)

- For linux (kamakiri attack), you need to recompile your linux kernel using this kernel patch :
```
sudo apt-get install build-essential libncurses-dev bison flex libssl-dev libelf-dev libdw-dev
git clone https://git.kernel.org/pub/scm/devel/pahole/pahole.git
cd pahole && mkdir build && cd build && cmake .. && make && sudo make install
sudo mv /usr/local/libdwarves* /usr/local/lib/ && sudo ldconfig
```

```
wget https://cdn.kernel.org/pub/linux/kernel/v5.x/linux-`uname -r`.tar.xz
tar xvf linux-`uname -r`.tar.xz
cd linux-`uname -r`
patch -p1 < ../Setup/kernelpatches/disable-usb-checks-5.10.patch
cp -v /boot/config-$(uname -r) .config
make menuconfig
make
sudo make modules_install 
sudo make install
```

- These aren't needed for current ubuntu (as make install will do, just for reference):

```
sudo update-initramfs -c -k `uname -r`
sudo update-grub
```

See Setup/kernels for ready-to-use kernel setups


- Reboot

```
sudo reboot
```

### Windows

#### Install python + git
- Install python 3.9 and git from Microsoft Store

- WIN+R ```cmd```

#### Grab files and install
```
git clone https://github.com/bkerler/mtkclient
cd mtkclient
pip3 install -r requirements.txt
```

#### Get latest zadig (>=2.5) and install WinUSB driver
- Get from https://zadig.akeo.ie
- Start zadig, select Options -> List all devices
- Connect powered off device via usb, and in list choose device with USB ID "0E8D""0003"
- Select WinUSB and press Button "Replace Driver"


## Compile payloads (optional)

### Install gcc armeabi compiler

```
sudo apt-get install gcc-arm-none-eabi
```

### Compile

See src/readme.build for detailed instructions.

```
cd src
make
```


## Usage

### Bypass SLA, DAA and SBC (using generic_patcher_payload)
`` 
./mtk payload
`` 
If you want to use SP Flash tool afterwards, make sure you select "UART" in the settings, not "USB".

### Dump brom
- Device has to be in bootrom mode, or da mode has to be crashed to enter damode
- if no option is given, either kamakiri or da will be used (da for insecure targets)
- if "kamakiri" is used as an option, kamakiri is enforced
- Valid options are : "kamakiri" (via usb_ctrl_handler attack), "amonet" (via gcpu)
  and "hashimoto" (via cqdma)

```
./mtk dumpbrom --ptype=["amonet","kamakiri","hashimoto"] [--filename=brom.bin]
```

### Dump preloader
- Device has to be in bootrom mode and preloader has to be intact on the device
```
./mtk dumppreloader --ptype=["amonet","kamakiri","kamakiri2","hashimoto"] [--filename=preloader.bin]
```


### Run original/patched preloader and disable sbc
- Boot in Brom or crash to Brom
```
./mtk plstage --preloader=preloader.bin
```

### Read memory using patched preloader
- Boot in Brom or crash to Brom
```
./mtk peek [addr] [length] --preloader=patched_preloader.bin
```

### Run custom payload

```
./mtk payload --payload=payload.bin [--var1=var1] [--wdt=wdt] [--uartaddr=addr] [--da_addr=addr] [--brom_addr=addr]
```

### Run stage2 in bootrom
`` 
./mtk stage
`` 

### Run stage2 in preloader
`` 
./mtk plstage
`` 

### Leave stage2 and reboot
`` 
./stage2 reboot
`` 

### Read rpmb in stage2 mode
`` 
./stage2 rpmb
`` 

### Read preloader in stage2 mode
`` 
./stage2 preloader
`` 

### Read memory as hex data in stage2 mode
`` 
./stage2 memread [start addr] [length]
`` 

### Read memory to file in stage2 mode
`` 
./stage2 memread [start addr] [length] --filename filename.bin
`` 

### Write hex data to memory in stage2 mode
`` 
./stage2 memwrite [start addr] --data [data as hexstring]
`` 

### Write memory from file in stage2 mode
`` 
./stage2 memwrite [start addr] --filename filename.bin
`` 

### Extract keys
`` 
./stage2 keys --mode [sej, dxcc]
`` 
For dxcc, you need to use plstage instead of stage

### Crash da in order to enter brom

```
./mtk crash [--vid=vid] [--pid=pid] [--interface=interface]
```

### Read flash

Dump boot partition to filename boot.bin via preloader

```
./mtk r boot boot.bin
```

Dump boot partition to filename boot.bin via bootrom

```
./mtk r boot boot.bin [--preloader=Loader/Preloader/your_device_preloader.bin]
```


Read full flash to filename flash.bin (use --preloader for brom)

```
./mtk rf flash.bin
```

Dump all partitions to directory "out". (use --preloader for brom)

```
./mtk rl out
```

Show gpt (use --preloader for brom)

```
./mtk printgpt
```


### Write flash
(use --preloader for brom)

Write filename boot.bin to boot partition

```
./mtk w boot boot.bin
```

Write filename flash.bin as full flash (currently only works in da mode)

```
./mtk wf flash.bin
```

Write all files in directory "out" to the flash partitions

```
./mtk wl out
```

### Erase flash

Erase boot partition (use --preloader for brom)
```
./mtk e boot
```

### I need logs !

- Run the mtk tool with --debugmode. Log will be written to log.txt (hopefully)

## Rules / Infos

### Chip details / configs
- Go to config/brom_config.py
- Unknown usb vid/pids for autodetection go to config/usb_ids.py
