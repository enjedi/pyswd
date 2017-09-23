"""devices.py
This is a collection of classes that represent available SWD hardware devices for use
with this library.

Each class is made up of relative information for a USB device and organized into a list
by device name, i.e. the class name.
"""

class Device(object):
    def __init__(self, description):
        self._description   = description
        self.ID_VENDOR      = None
        self.ID_PRODUCT     = None
        self.PIPE_OUT       = None
        self.PIPE_IN        = None

    def __str__(self):
        return self._description


class STLinkV2(Device):
    """ST-Link/V2 USB Device"""
    def __init__(self, description):
        super().__init__(description)
        self.ID_VENDOR   = 0x0483
        self.ID_PRODUCT  = 0x3748
        self.PIPE_OUT    = 0x02
        self.PIPE_IN     = 0x81


class STLinkV21(Device):
    """ST-Link/V2-1 USB Device"""
    def __init__(self, description):
        super().__init__(description)
        self.ID_VENDOR   = 0x0483
        self.ID_PRODUCT  = 0x374b
        self.PIPE_OUT    = 0x01
        self.PIPE_IN     = 0x81


DEVICE_LIST = {
    STLinkV2.__name__   : STLinkV2("STLink V2"),
    STLinkV21.__name__  : STLinkV21("STLink V2-1")
}
