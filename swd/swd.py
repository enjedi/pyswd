"""swd.py
SWD functionality for Python. This commandeers USB protocols of third-party hardware
devices and uses them for general SWD use.
"""

import usbcom


class SWDException(Exception):
    """Exception raised for general SWD issues."""


class InvalidFrequencyError(SWDException):
    pass


class SWD():
    """ST-Link protocol"""
    def __init__(self, **kwargs):
        """Initialize SWD communication and sanity check connection.

        :kwarg device:  Device type to use for communication
        :kwarg speed:   Desired SWD frequency in KHz
        """
        self._comm = usbcom.USBCom(kwargs.get("device"))
        self._dev = self._comm.get_device()
        self.leave_state()
        self._set_swd_freq(kwargs.get("speed"))
        self.enter_debug_swd()
        self._coreid = hex(self.get_coreid())

    @property
    def comm(self):
        """Communication class"""
        return self._comm

    def leave_state(self):
        """Leave current state of ST-Link"""
        r = self._comm.xfer([self._dev.CMD.GET_CURRENT_MODE], rx_len=2)
        if r[0] == self._dev.MODE.DFU:
            cmd = [self._dev.CMD.DFU, self._dev.DFU.EXIT]
        elif r[0] == self._dev.MODE.DEBUG:
            cmd = [self._dev.CMD.DEBUG, self._dev.DEBUG.EXIT]
        elif r[0] == self._dev.MODE.SWIM:
            cmd = [self._dev.CMD.SWIM, self._dev.SWIM.EXIT]
        else:
            return
        self._comm.xfer(cmd)

    def _set_swd_freq(self, frequency=None):
        """Set SWD frequency.

        Defaults to device DEFAULT if None.

        :param frequency: Desired SWD frequency, in KHz.
        """
        if not frequency:
            frequency = self._dev.FREQUENCY.DEFAULT

        data = self._dev.FREQUENCY.MAP.get(frequency)
        if not data:
            raise InvalidFrequencyError("Frequency '{}' is not supported.".format(frequency))

        cmd = [self._dev.CMD.DEBUG, self._dev.DEBUG.A2.SWD_SET_FREQ, data]
        res = self._comm.xfer(cmd, rx_len=2)
        if res[0] != 0x80:
            raise usbcom.USBComException("Error when switching SWD frequency.")

    def get_target_voltage(self):
        """Get target voltage from device"""
        res = self._comm.xfer([self._dev.CMD.GET_TARGET_VOLTAGE], rx_len=8)
        an0 = int.from_bytes(res[:4], byteorder='little')
        an1 = int.from_bytes(res[4:8], byteorder='little')
        return round(2 * an1 * 1.2 / an0, 3) if an0 != 0 else None

    def enter_debug_swd(self):
        """Enter SWD debug mode"""
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.A2.ENTER,
            self._dev.DEBUG.ENTER_SWD]
        self._comm.xfer(cmd, rx_len=2)

    def get_coreid(self):
        """Get core ID from MCU"""
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.READCOREID]
        res = self._comm.xfer(cmd, rx_len=4)
        return int.from_bytes(res[:4], byteorder='little')

    def get_reg(self, reg):
        """Get core register"""
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.A2.READREG,
            reg]
        res = self._comm.xfer(cmd, rx_len=8)
        return int.from_bytes(res[4:8], byteorder='little')

    def set_reg(self, reg, data):
        """Set core register"""
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.A2.WRITEREG,
            reg]
        cmd.extend(list(data.to_bytes(4, byteorder='little')))
        self._comm.xfer(cmd, rx_len=2)

    def set_mem32(self, addr, data):
        """Set memory register (32 bits)"""
        if addr % 4:
            raise SWDException('address is not in multiples of 4')
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.A2.WRITEDEBUGREG]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(data.to_bytes(4, byteorder='little')))
        self._comm.xfer(cmd, rx_len=2)

    def get_mem32(self, addr):
        """Get memory register (32 bits)"""
        if addr % 4:
            raise SWDException('address is not in multiples of 4')
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.A2.READDEBUGREG]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        res = self._comm.xfer(cmd, rx_len=8)
        return int.from_bytes(res[4:8], byteorder='little')

    def read_mem32(self, addr, size):
        """Read memory (32 bits access)"""
        if addr % 4:
            raise SWDException('Address must be in multiples of 4')
        if size % 4:
            raise SWDException('Size must be in multiples of 4')
        if size > self._dev.MAXIMUM_TRANSFER_SIZE:
            raise SWDException('Size is larger than maximum')
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.READMEM_32BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(size.to_bytes(4, byteorder='little')))
        return self._comm.xfer(cmd, rx_len=size)

    def write_mem32(self, addr, data):
        """Write memory (32 bits access)"""
        if addr % 4:
            raise SWDException('Address must be in multiples of 4')
        if len(data) % 4:
            raise SWDException('Size must be in multiples of 4')
        if len(data) > self._dev.MAXIMUM_TRANSFER_SIZE:
            raise SWDException('Size is larger than maximum')
        cmd = [
            self._dev.CMD.DEBUG,
            self._dev.DEBUG.WRITEMEM_32BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(len(data).to_bytes(4, byteorder='little')))
        self._comm.xfer(cmd, data=data)

    def read_mem8(self, addr, size):
        """Read memory (8 bits access)"""
        if size > self._dev.MAXIMUM_8BIT_DATA:
            raise SWDException('Too much bytes to read')
        cmd = [self._dev.CMD.DEBUG, self._dev.DEBUG.READMEM_8BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(size.to_bytes(4, byteorder='little')))
        return self._comm.xfer(cmd, rx_len=size)

    def write_mem8(self, addr, data):
        """Write memory (8 bits access)"""
        if len(data) > self._dev.MAXIMUM_8BIT_DATA:
            raise SWDException('Too much bytes to write')
        cmd = [self._dev.CMD.DEBUG, self._dev.DEBUG.WRITEMEM_8BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(len(data).to_bytes(4, byteorder='little')))
        self._comm.xfer(cmd, data=data)

if __name__ == "__main__":
    swd = SWD()
    print(swd.get_target_voltage())
