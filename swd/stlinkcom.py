"""usb_com.py
USB communication between the host and SWD hardware device.
"""
import usb.core
from swd_devices import DEVICE_LIST


class USBComException(Exception):
    """Exception raised for errors in USB communication to an SWD device."""


class DeviceNotFoundError(USBComException):
    """Exception raised for when no STLink device is connected."""


class USBComDevice():
    """ USB device communication class"""
    def __init__(self, device):
        dev = DEVICE_LIST.get(device)
        try:
            self._dev = usb.core.find(idVendor=dev.ID_VENDOR, idProduct=dev.ID_PRODUCT)
        except AttributeError:
            pass
        if self._dev is None:
            raise DeviceNotFoundError()
        self.PIPE_OUT = dev.PIPE_OUT
        self.PIPE_IN = dev.PIPE_IN

    def write(self, data, timeout=200):
        """Write data to USB pipe"""
        count = self._dev.write(self.PIPE_OUT, data, timeout)
        if count != len(data):
            raise USBComException("Error Sending data")

    def read(self, size, timeout=200):
        """Read data from USB pipe"""
        read_size = size
        if read_size < 64:
            read_size = 64
        elif read_size % 4:
            read_size += 3
            read_size &= 0xffc
        data = self._dev.read(self.PIPE_IN, read_size, timeout).tolist()
        return data[:size]




class STLinkCom():
    """ST-Link communication class"""
    STLINK_CMD_SIZE = 16
    COM_CLASSES     = [STLinkV2UsbCom, STLinkV21UsbCom]

    def __init__(self):
        self._dev = None
        for com_cls in self.COM_CLASSES:
            try:
                self._dev = com_cls()
                break
            except DeviceNotFoundError:
                continue
        else:
            raise DeviceNotFoundError()

    def get_version(self):
        """Get device version"""
        return self._dev.DEV_NAME

    def xfer(self, cmd, data=None, rx_len=0, timeout=200):
        """Transfer command between ST-Link"""
        try:
            if len(cmd) > self.STLINK_CMD_SIZE:
                raise STLinkComException("Error too many Bytes in command")
            # pad to STLINK_CMD_SIZE
            cmd += [0] * (self.STLINK_CMD_SIZE - len(cmd))
            self._dev.write(cmd, timeout)
            if data:
                self._dev.write(data, timeout)
            if rx_len:
                return self._dev.read(rx_len)
        except usb.core.USBError as err:
            raise STLinkComException("USB Error: %s" % err)
        return None
