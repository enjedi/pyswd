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
        self.VERSION = dev.VERSION

    def write(self, data, timeout=200):
        """Write data to USB pipe"""
        count = self._dev.write(self.PIPE_OUT, data, timeout)
        if count != len(data):
            raise USBComException("USB Error when sending data")

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


class USBCom():
    """Main USB communication class"""
    CMD_SIZE_BYTES = 16

    def __init__(self):
        for device in iter(DEVICE_LIST):
            try:
                self._dev = USBComDevice(device)
                break
            except DeviceNotFoundError:
                continue
        else:
            raise DeviceNotFoundError("No known SWD devices found.")

    def get_version(self):
        """Get device version"""
        return self._dev.VERSION

    def xfer(self, cmd, data=None, rx_len=0, timeout=200):
        """Transfer command between ST-Link.

        Written command is padded for CMD_SIZE_BYTES
        """
        try:
            if len(cmd) > self.CMD_SIZE_BYTES:
                raise USBComException("USB Error: Too many bytes in command")
            cmd += [0] * (self.CMD_SIZE_BYTES - len(cmd))
            self._dev.write(cmd, timeout)
            if data:
                self._dev.write(data, timeout)
            if rx_len:
                return self._dev.read(rx_len)
        except usb.core.USBError as err:
            raise USBComException("USB Error: {}".format(err))
        return None
