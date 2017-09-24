# PYSWD

## Introduction

The goal of this module is to provide functional SWD using third-party, off-the-shelf
hardware devices.

As this is designed to provide general SWD use via Python, it is not locked to interacting
with any particular architecture. It's functionality is only dependent upon the firmware
of the host SWD device.

This has been developed and tested primarily with Python3.5 on Debian-based Linux.

## Installation

This installation procedure is targeted for Debian-based Linux distributions.

### Dependencies

* libusb-1.0.0
* [PyUSB 1.0](https://github.com/walac/pyusb)

Install the basic packages:

```
sudo apt-get install python3-dev libusb-1.0.0
```

[Install PyUSB](https://github.com/walac/pyusb).

For system-wide installation of this module:

```
sudo python setup.py install
```

For only local user installation:

```
python setup.py install --user
```

## Example Use

The full example is embedded as the `__main__` call to `python swd/swd.py`.

General Python scripts can call on it as any other module:

```
>>> import swd
>>> s = swd.SWD()
```

By default, SWD will acquire the first available device in its list of known devices and
use 1.8MHz as the default frequency.
This can be altered by specifying device and/or frequency (in KHz) through keyword arguments:

```
>>> s = swd.SWD(device=STLink/V2, speed=1800)
```

A list of known hardware devices can also be returned:

```
>>> s.comm.get_device_list()
['STLink/V2', 'STLink/V2-1']
```

---

## Credit

This project is a fork of
[pavelrevak's pyswd project](https://github.com/pavelrevak/pyswd),
and has been retrofitted for my own tastes and functionality desires.
