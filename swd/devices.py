"""devices.py
This is a collection of classes that represent available SWD hardware devices for use
with this library.

Each class is made up of relative information for a USB device and organized into a list
by device name, i.e. the class name.
"""

class STLinkV2():
    """ST-Link/V2 USB Device"""
    ID_VENDOR   = 0x0483
    ID_PRODUCT  = 0x3748
    PIPE_OUT    = 0x02
    PIPE_IN     = 0x81
    VERSION     = "V2"


class STLinkV21():
    """ST-Link/V2-1 USB Device"""
    ID_VENDOR   = 0x0483
    ID_PRODUCT  = 0x374b
    PIPE_OUT    = 0x01
    PIPE_IN     = 0x81
    VERSION     = "V2-1"


DEVICE_LIST = {
    STLinkV2.__name__   : STLinkV2(),
    STLinkV21.__name__  : STLinkV21()
}
