"""ST-Link/V2 protocol"""

import swd.stlinkcom as stlinkcom

class STLinkException(Exception):
    """Exception raised for general issues in the STLink class."""


class STLink():
    """ST-Link protocol"""
    class STLinkVersion():
        """ST-Link version holder class"""
        def __init__(self, dev_ver, ver):
            self._stlink = (ver >> 12) & 0xf
            self._jtag = (ver >> 6) & 0x3f
            self._swim = ver & 0x3f if dev_ver == 'V2' else None
            self._mass = ver & 0x3f if dev_ver == 'V2-1' else None
            self._api = 2 if self._jtag > 11 else 1
            self._str = "ST-Link/%s V%dJ%d" % (dev_ver, self._stlink, self._jtag)
            if dev_ver == 'V2':
                self._str += "S%d" % self._swim
            if dev_ver == 'V2-1':
                self._str += "M%d" % self._mass

        @property
        def stlink(self):
            """Major version"""
            return self._stlink

        @property
        def jtag(self):
            """Jtag version"""
            return self._jtag

        @property
        def swim(self):
            """SWIM version"""
            return self._swim

        @property
        def mass(self):
            """Mass storage version"""
            return self._mass

        @property
        def api(self):
            """API version"""
            return self._api

        @property
        def str(self):
            """String representation"""
            return self._str


    def __init__(self, swd_frequency=1800000):
        self._com = stlinkcom.STLinkCom()
        self._version = self.get_version()
        self.leave_state()
        # self._target_volgtage = self.read_target_voltage()
        if self._version.jtag >= 22:
            self._set_swd_freq(swd_frequency)
        self.enter_debug_swd()
        # self._coreid = self.get_coreid()

    @property
    def com(self):
        """Communication class"""
        return self._com

    @property
    def version(self):
        """ST-Link version"""
        return self._version

    def get_version(self):
        """Read and decode version from ST-Link"""
        res = self._com.xfer([STLink.STLINK_GET_VERSION, 0x80], rx_len=6)
        dev_ver = self._com.get_version()
        ver = int.from_bytes(res[:2], byteorder='big')
        return STLink.STLinkVersion(dev_ver, ver)

    def leave_state(self):
        """Leave current state of ST-Link"""
        res = self._com.xfer([STLink.STLINK_GET_CURRENT_MODE], rx_len=2)
        if res[0] == STLink.STLINK_MODE_DFU:
            cmd = [STLink.STLINK_DFU_COMMAND, STLink.STLINK_DFU_EXIT]
        elif res[0] == STLink.STLINK_MODE_DEBUG:
            cmd = [STLink.STLINK_DEBUG_COMMAND, STLink.STLINK_DEBUG_EXIT]
        elif res[0] == STLink.STLINK_MODE_SWIM:
            cmd = [STLink.STLINK_SWIM_COMMAND, STLink.STLINK_SWIM_EXIT]
        else:
            return
        self._com.xfer(cmd)

    def _set_swd_freq(self, frequency=1800000):
        """Set SWD frequency"""
        for freq, data in STLink.STLINK_DEBUG_A2_SWD_FREQ_MAP.items():
            if frequency >= freq:
                cmd = [
                    STLink.STLINK_DEBUG_COMMAND,
                    STLink.STLINK_DEBUG_A2_SWD_SET_FREQ,
                    data]
                res = self._com.xfer(cmd, rx_len=2)
                if res[0] != 0x80:
                    raise STLinkException("Error switching SWD frequency")
                return
        raise STLinkException("Selected SWD frequency is too low")

    def get_target_voltage(self):
        """Get target voltage from programmer"""
        res = self._com.xfer([STLink.STLINK_GET_TARGET_VOLTAGE], rx_len=8)
        an0 = int.from_bytes(res[:4], byteorder='little')
        an1 = int.from_bytes(res[4:8], byteorder='little')
        return 2 * an1 * 1.2 / an0 if an0 != 0 else None

    def enter_debug_swd(self):
        """Enter SWD debug mode"""
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_A2_ENTER,
            STLink.STLINK_DEBUG_ENTER_SWD]
        self._com.xfer(cmd, rx_len=2)

    def get_coreid(self):
        """Get core ID from MCU"""
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_READCOREID]
        res = self._com.xfer(cmd, rx_len=4)
        return int.from_bytes(res[:4], byteorder='little')

    def get_reg(self, reg):
        """Get core register"""
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_A2_READREG,
            reg]
        res = self._com.xfer(cmd, rx_len=8)
        return int.from_bytes(res[4:8], byteorder='little')

    def set_reg(self, reg, data):
        """Set core register"""
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_A2_WRITEREG,
            reg]
        cmd.extend(list(data.to_bytes(4, byteorder='little')))
        self._com.xfer(cmd, rx_len=2)

    def set_mem32(self, addr, data):
        """Set memory register (32 bits)"""
        if addr % 4:
            raise STLinkException('address is not in multiples of 4')
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_A2_WRITEDEBUGREG]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(data.to_bytes(4, byteorder='little')))
        self._com.xfer(cmd, rx_len=2)

    def get_mem32(self, addr):
        """Get memory register (32 bits)"""
        if addr % 4:
            raise STLinkException('address is not in multiples of 4')
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_A2_READDEBUGREG]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        res = self._com.xfer(cmd, rx_len=8)
        return int.from_bytes(res[4:8], byteorder='little')

    def read_mem32(self, addr, size):
        """Read memory (32 bits access)"""
        if addr % 4:
            raise STLinkException('Address must be in multiples of 4')
        if size % 4:
            raise STLinkException('Size must be in multiples of 4')
        if size > STLink.STLINK_MAXIMUM_TRANSFER_SIZE:
            raise STLinkException('Too much bytes to read')
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_READMEM_32BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(size.to_bytes(4, byteorder='little')))
        return self._com.xfer(cmd, rx_len=size)

    def write_mem32(self, addr, data):
        """Write memory (32 bits access)"""
        if addr % 4:
            raise STLinkException('Address must be in multiples of 4')
        if len(data) % 4:
            raise STLinkException('Size must be in multiples of 4')
        if len(data) > STLink.STLINK_MAXIMUM_TRANSFER_SIZE:
            raise STLinkException('Too much bytes to write')
        cmd = [
            STLink.STLINK_DEBUG_COMMAND,
            STLink.STLINK_DEBUG_WRITEMEM_32BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(len(data).to_bytes(4, byteorder='little')))
        self._com.xfer(cmd, data=data)

    def read_mem8(self, addr, size):
        """Read memory (8 bits access)"""
        if size > STLink.STLINK_MAXIMUM_8BIT_DATA:
            raise STLinkException('Too much bytes to read')
        cmd = [STLink.STLINK_DEBUG_COMMAND, STLink.STLINK_DEBUG_READMEM_8BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(size.to_bytes(4, byteorder='little')))
        return self._com.xfer(cmd, rx_len=size)

    def write_mem8(self, addr, data):
        """Write memory (8 bits access)"""
        if len(data) > STLink.STLINK_MAXIMUM_8BIT_DATA:
            raise STLinkException('Too much bytes to write')
        cmd = [STLink.STLINK_DEBUG_COMMAND, STLink.STLINK_DEBUG_WRITEMEM_8BIT]
        cmd.extend(list(addr.to_bytes(4, byteorder='little')))
        cmd.extend(list(len(data).to_bytes(4, byteorder='little')))
        self._com.xfer(cmd, data=data)
