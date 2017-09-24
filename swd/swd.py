"""swd.py
SWD functionality for Python. This commandeers USB protocols of third-party hardware
devices and uses them for general SWD use.
"""

import usbcom


class SWDException(Exception):
    """Exception raised for general SWD issues."""


class SWD():
    """ST-Link protocol"""
    def __init__(self, use_device=None):
        self._comm = usbcom.USBCom(use_device)
#        self.leave_state()
#        self._target_volgtage = self.read_target_voltage()
#        if self._version.jtag >= 22:
#            self._set_swd_freq(swd_frequency)
#        self.enter_debug_swd()
#         self._coreid = self.get_coreid()

    @property
    def comm(self):
        """Communication class"""
        return self._comm

#    def leave_state(self):
#        """Leave current state of ST-Link"""
#        res = self._com.xfer([STLink.STLINK_GET_CURRENT_MODE], rx_len=2)
#        if res[0] == STLink.STLINK_MODE_DFU:
#            cmd = [STLink.STLINK_DFU_COMMAND, STLink.STLINK_DFU_EXIT]
#        elif res[0] == STLink.STLINK_MODE_DEBUG:
#            cmd = [STLink.STLINK_DEBUG_COMMAND, STLink.STLINK_DEBUG_EXIT]
#        elif res[0] == STLink.STLINK_MODE_SWIM:
#            cmd = [STLink.STLINK_SWIM_COMMAND, STLink.STLINK_SWIM_EXIT]
#        else:
#            return
#        self._com.xfer(cmd)

#    def _set_swd_freq(self, frequency=1800000):
#        """Set SWD frequency"""
#        for freq, data in STLink.STLINK_DEBUG_A2_SWD_FREQ_MAP.items():
#            if frequency >= freq:
#                cmd = [
#                    STLink.STLINK_DEBUG_COMMAND,
#                    STLink.STLINK_DEBUG_A2_SWD_SET_FREQ,
#                    data]
#                res = self._com.xfer(cmd, rx_len=2)
#                if res[0] != 0x80:
#                    raise STLinkException("Error switching SWD frequency")
#                return
#        raise STLinkException("Selected SWD frequency is too low")
#
#    def get_target_voltage(self):
#        """Get target voltage from programmer"""
#        res = self._com.xfer([STLink.STLINK_GET_TARGET_VOLTAGE], rx_len=8)
#        an0 = int.from_bytes(res[:4], byteorder='little')
#        an1 = int.from_bytes(res[4:8], byteorder='little')
#        return 2 * an1 * 1.2 / an0 if an0 != 0 else None
#
#    def enter_debug_swd(self):
#        """Enter SWD debug mode"""
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_A2_ENTER,
#            STLink.STLINK_DEBUG_ENTER_SWD]
#        self._com.xfer(cmd, rx_len=2)
#
#    def get_coreid(self):
#        """Get core ID from MCU"""
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_READCOREID]
#        res = self._com.xfer(cmd, rx_len=4)
#        return int.from_bytes(res[:4], byteorder='little')
#
#    def get_reg(self, reg):
#        """Get core register"""
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_A2_READREG,
#            reg]
#        res = self._com.xfer(cmd, rx_len=8)
#        return int.from_bytes(res[4:8], byteorder='little')
#
#    def set_reg(self, reg, data):
#        """Set core register"""
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_A2_WRITEREG,
#            reg]
#        cmd.extend(list(data.to_bytes(4, byteorder='little')))
#        self._com.xfer(cmd, rx_len=2)
#
#    def set_mem32(self, addr, data):
#        """Set memory register (32 bits)"""
#        if addr % 4:
#            raise STLinkException('address is not in multiples of 4')
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_A2_WRITEDEBUGREG]
#        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
#        cmd.extend(list(data.to_bytes(4, byteorder='little')))
#        self._com.xfer(cmd, rx_len=2)
#
#    def get_mem32(self, addr):
#        """Get memory register (32 bits)"""
#        if addr % 4:
#            raise STLinkException('address is not in multiples of 4')
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_A2_READDEBUGREG]
#        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
#        res = self._com.xfer(cmd, rx_len=8)
#        return int.from_bytes(res[4:8], byteorder='little')
#
#    def read_mem32(self, addr, size):
#        """Read memory (32 bits access)"""
#        if addr % 4:
#            raise STLinkException('Address must be in multiples of 4')
#        if size % 4:
#            raise STLinkException('Size must be in multiples of 4')
#        if size > STLink.STLINK_MAXIMUM_TRANSFER_SIZE:
#            raise STLinkException('Too much bytes to read')
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_READMEM_32BIT]
#        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
#        cmd.extend(list(size.to_bytes(4, byteorder='little')))
#        return self._com.xfer(cmd, rx_len=size)
#
#    def write_mem32(self, addr, data):
#        """Write memory (32 bits access)"""
#        if addr % 4:
#            raise STLinkException('Address must be in multiples of 4')
#        if len(data) % 4:
#            raise STLinkException('Size must be in multiples of 4')
#        if len(data) > STLink.STLINK_MAXIMUM_TRANSFER_SIZE:
#            raise STLinkException('Too much bytes to write')
#        cmd = [
#            STLink.STLINK_DEBUG_COMMAND,
#            STLink.STLINK_DEBUG_WRITEMEM_32BIT]
#        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
#        cmd.extend(list(len(data).to_bytes(4, byteorder='little')))
#        self._com.xfer(cmd, data=data)
#
#    def read_mem8(self, addr, size):
#        """Read memory (8 bits access)"""
#        if size > STLink.STLINK_MAXIMUM_8BIT_DATA:
#            raise STLinkException('Too much bytes to read')
#        cmd = [STLink.STLINK_DEBUG_COMMAND, STLink.STLINK_DEBUG_READMEM_8BIT]
#        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
#        cmd.extend(list(size.to_bytes(4, byteorder='little')))
#        return self._com.xfer(cmd, rx_len=size)
#
#    def write_mem8(self, addr, data):
#        """Write memory (8 bits access)"""
#        if len(data) > STLink.STLINK_MAXIMUM_8BIT_DATA:
#            raise STLinkException('Too much bytes to write')
#        cmd = [STLink.STLINK_DEBUG_COMMAND, STLink.STLINK_DEBUG_WRITEMEM_8BIT]
#        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
#        cmd.extend(list(len(data).to_bytes(4, byteorder='little')))
#        self._com.xfer(cmd, data=data)

if __name__ == "__main__":
    swd = SWD()
