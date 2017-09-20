"""ST-Link/V2 USB communication"""

import usb.core
# import usb.util


class STLinkComException(Exception):
    """Exception"""


class STLinkNotFound(Exception):
    """Exception"""


class STLinkV2UsbCom():
    """ST-Link/V2 USB communication class"""
    ID_VENDOR = 0x0483
    ID_PRODUCT = 0x3748
    PIPE_OUT = 0x02
    PIPE_IN = 0x81
    DEV_NAME = "V2"

    def __init__(self):
        self._dev = None
        for dev in usb.core.find(find_all=True):
            if dev.idVendor == self.ID_VENDOR and dev.idProduct == self.ID_PRODUCT:
                self._dev = dev
                return
        raise STLinkNotFound()

    def write(self, data, tout=200):
        """Write data to USB pipe"""
        count = self._dev.write(self.PIPE_OUT, data, tout)
        if count != len(data):
            raise STLinkComException("Error Sending data")

    def read(self, size, tout=200):
        """Read data from USB pipe"""
        read_size = size
        if read_size < 64:
            read_size = 64
        elif read_size % 4:
            read_size += 3
            read_size &= 0xffc
        data = self._dev.read(self.PIPE_IN, read_size, tout).tolist()
        return data[:size]


class STLinkV21UsbCom(STLinkV2UsbCom):
    """ST-Link/V2-1 USB communication"""
    ID_VENDOR = 0x0483
    ID_PRODUCT = 0x374b
    PIPE_OUT = 0x01
    PIPE_IN = 0x81
    DEV_NAME = "V2-1"


class STLinkCom():
    """ST-Link communication class"""
    STLINK_CMD_SIZE = 16
    COM_CLASSES = [STLinkV2UsbCom, STLinkV21UsbCom]

    def __init__(self):
        self._dev = None
        for com_cls in self.COM_CLASSES:
            try:
                self._dev = com_cls()
                break
            except STLinkNotFound:
                continue
        else:
            raise STLinkNotFound()

    def get_version(self):
        """Get device version"""
        return self._dev.DEV_NAME

    def xfer(self, cmd, data=None, rx_len=0, tout=200):
        """Transfer command between ST-Link"""
        try:
            if len(cmd) > self.STLINK_CMD_SIZE:
                raise STLinkComException("Error too many Bytes in command")
            # pad to STLINK_CMD_SIZE
            cmd += [0] * (self.STLINK_CMD_SIZE - len(cmd))
            self._dev.write(cmd, tout)
            if data:
                self._dev.write(data, tout)
            if rx_len:
                return self._dev.read(rx_len)
        except usb.core.USBError as err:
            raise STLinkComException("USB Error: %s" % err)
        return None
