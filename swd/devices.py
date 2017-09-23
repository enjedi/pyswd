"""devices.py
This is a collection of classes that represent available SWD hardware devices for use
with this library.

Each class is made up of relative information for a USB device and organized into a list
by device name, i.e. the class name.
"""

class Device(object):
    """Prototype class for SWD devices.

    Default MAX sizes are defaulted to STLink device values.
    """
    def __init__(self, description):
        self._description       = description
        self.ID_VENDOR          = None
        self.ID_PRODUCT         = None
        self.PIPE_OUT           = None
        self.PIPE_IN            = None
        self.MAX_TRANSFER_SIZE  = 1024
        self.MAX_8BIT_DATA      = 64

    def __str__(self):
        return self._description


class STLink(Device):
    """ST-Link USB Device.

    Compatible STLink device versions are V2 and V2-1.
    """
    def __init__(self, version):
        """Initialize a given STLink based on version.

        :param version: Device version string (STLink/<ver> in list of attached USB devices)
        """
        super().__init__("{0}/{1}".format("STLink", version))
        self.ID_VENDOR   = 0x0483
        self.ID_PRODUCT  = 0x374b if version == "V2-1" else 0x3748
        self.PIPE_OUT    = 0x01 if version == "V2-1" else 0x02
        self.PIPE_IN     = 0x81

    class CMD():
        """Enumeration of command codes."""
        GET_VERSION         = 0xf1
        DEBUG               = 0xf2
        DFU                 = 0xf3
        SWIM                = 0xf4
        GET_CURRENT_MODE    = 0xf5
        GET_TARGET_VOLTAGE  = 0xf7

    class MODE():
        """Enumeration of operation mode codes."""
        (DFU,
        MASS,
        DEBUG,
        SWIM,
        BOOTLOADER) = range(0, 5)

    class DFU():
        """Enumeration of DFU codes."""
        EXIT = 0x07

    class SWIM():
        """Enumeration of SWIM codes."""
        ENTER = 0x00
        EXIT  = 0x01

    class DEBUG():
        """Enumeration of Debug codes."""
        ENTER_JTAG      = 0x00
        STATUS          = 0x01
        FORCEDEBUG      = 0x02
        READMEM_32BIT   = 0x07
        WRITEMEM_32BIT  = 0x08
        RUNCORE         = 0x09
        STEPCORE        = 0x0a
        READMEM_8BIT    = 0x0c
        WRITEMEM_8BIT   = 0x0d
        EXIT            = 0x21
        READCOREID      = 0x22
        SYNC            = 0x3e
        ENTER_SWD       = 0xa3

        class A1():
            """Enumeration of Debug A1 codes."""
            RESETSYS         = 0x03
            READALLREGS      = 0x04
            READREG          = 0x05
            WRITEREG         = 0x06
            SETFP            = 0x0b
            CLEARFP          = 0x0e
            WRITEDEBUGREG    = 0x0f
            SETWATCHPOINT    = 0x10
            ENTER            = 0x20

        class A2():
            """Enumeration of Debug A2 codes."""
            NRST_LOW         = 0x00
            NRST_HIGH        = 0x01
            NRST_PULSE       = 0x02
            ENTER            = 0x30
            READ_IDCODES     = 0x31
            RESETSYS         = 0x32
            READREG          = 0x33
            WRITEREG         = 0x34
            WRITEDEBUGREG    = 0x35
            READDEBUGREG     = 0x36
            READALLREGS      = 0x3a
            GETLASTRWSTATUS  = 0x3b
            DRIVE_NRST       = 0x3c
            START_TRACE_RX   = 0x40
            STOP_TRACE_RX    = 0x41
            GET_TRACE_NB     = 0x42
            SWD_SET_FREQ     = 0x43

    class FREQUENCY():
        """Enumeration of available SWD frequencies.

        Default frequency is 1.8MHz
        """
        DEFAULT = 1,
        MAP = {
            4000000: 0,
            1800000: 1,
            1200000: 2,
            950000:  3,
            480000:  7,
            240000: 15,
            125000: 31,
            100000: 40,
            50000:  79,
            25000: 158,
            # 15000: 265,
            # 5000:  798
        }


DEVICE_LIST = {
    "STLink/V2"   : STLink("V2"),
    "STLink/V2-1" : STLink("V2-1")
}
