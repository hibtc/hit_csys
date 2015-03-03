"""
Low level wrapper for the HIT accelerator control software.

Wraps the API of the 'BeamOptikDLL.dll' library to a more pythonic
interface.
"""

from collections import namedtuple
from ctypes import c_double as Double, c_char_p as Str, c_int as Int
import ctypes
import logging


EFI = namedtuple('EFI', ['energy', 'focus', 'intensity', 'gantry_angle'])


class _EnumBase(int):

    """Abstract base type for enums (missed :cvar:`_value_names`)."""

    def __repr__(self):
        return '<{}.{}: {}>'.format(
            self.__class__.__name__,
            self._value_names[int(self)],
            int(self),
        )


def make_enum(name, value_names):
    """Create a simple enum type (like in C++)."""
    Enum = type(name, (_EnumBase,), {
        '_value_names': value_names,
    })
    for i, v in enumerate(value_names):
        setattr(Enum, v, Enum(i))
    return Enum


DVMStatus = make_enum('DVMStatus', [
    'Stop', 'Idle', 'Init', 'Ready', 'Busy', 'Finish', 'Error'
])
GetOptions = make_enum('GetOptions', [
    'Current', 'Saved'
])
ExecOptions = make_enum('ExecOptions', [
    'CalcAll', 'CalcDif', 'SimplyStore'
])
GetSDOptions = make_enum('GetSDOptions', [
    'Current', 'Database', 'Test'
])


class BeamOptikDLL(object):

    """
    Thin wrapper around the BeamOptikDLL API.

    It abstracts the ctypes data types and automates InterfaceId as well as
    iDone. Nothing else.

    Instanciation is a two-step process as follows:

    >>> obj = BeamOptikDLL.load_library()
    >>> obj.GetInterfaceInstance()
    """

    #----------------------------------------
    # internal methods
    #----------------------------------------

    error_messages = [
        None,
        "Invalid Interface ID.",
        "Parameter not found in internal DVM list.",
        "GetValue failed.",
        "SetValue failed.",
        "Unknown option.",
        "Memory error.",
        "General runtime error.",
        "Ramp event not supported.",
        "Ramp data not available.",
        "Invalid offset for ramp function."]

    @classmethod
    def check_return(cls, done):
        """
        Check DLL-API exit code for errors and raise exception.

        :param int done: exit code of an DLL function
        :raises RuntimeError: if the exit code is a known error code != 0
        :raises ValueError: if the exit code is unknown
        """
        if 0 < done and done < len(cls.error_messages):
            raise RuntimeError(cls.error_messages[done])
        elif done != 0:
            raise ValueError("Unknown error: %i" % done)

    def _call(self, function, *params):
        """
        Call the specified DLL function.

        :param str function: name of the function to call
        :param params: ctype function parameters except for piDone.
        :raises RuntimeError: if the exit code indicates any error

        For internal use only!
        """
        done = Int()
        params = list(params)
        if function == 'SelectMEFI':
            params.insert(6, done)
        else:
            params.append(done)
        def param(p):
            return p if isinstance(p, Str) else ctypes.byref(p)
        getattr(self.lib, function)(*map(param, params))
        self.check_return(done.value)

    #----------------------------------------
    # things that don't require IID to be set:
    #----------------------------------------

    @classmethod
    def load_library(cls, filename='BeamOptikDLL.dll'):
        """
        Search for the DLL in PATH and return a BeamOptikDLL wrapper object.
        """
        try:
            return cls(ctypes.windll.LoadLibrary(filename))
        except AttributeError:
            raise OSError

    def DisableMessageBoxes(self):
        """
        Prevent creation of certain message boxes.

        :raises RuntimeError: if the exit code indicates any error
        """
        self._call('DisableMessageBoxes')

    def GetInterfaceInstance(self):
        """
        Initialize a BeamOptikDLL instance (connects DB and initialize DLL).

        :return: new instance id
        :rtype: int
        :raises RuntimeError: if the exit code indicates any error
        """
        if self._iid is not None:
            raise RuntimeError("GetInterfaceInstance cannot be called twice.")
        iid = Int()
        self._call('GetInterfaceInstance', iid)
        self._iid = iid
        return iid

    @property
    def lib(self):
        """Shared library proxy."""
        return self._lib

    #----------------------------------------
    # object API
    #----------------------------------------

    def __init__(self, lib):
        """
        Initialize member variables.

        Usually, you want to use :classmethod:`load_library` to create
        instances instead of directly invoking this constructor.

        :param lib: shared library proxy object
        """
        self._lib = lib
        self._iid = None
        self._selected_vacc = None
        self._selected_efi = EFI(None, None, None, None)
        self._logger = logging.getLogger(__name__)

    @property
    def iid(self):
        """Interface instance ID."""
        if self._iid is None:
            raise RuntimeError("GetInterfaceInstance must be called before using other methods.")
        return self._iid

    def __bool__(self):
        """Check if the object belongs to an initialized interface instance."""
        return self._iid is not None

    __nonzero__ = __bool__

    def FreeInterfaceInstance(self):
        """
        Free resources.

        :raises RuntimeError: if the exit code indicates any error
        """
        self._call('FreeInterfaceInstance', self.iid)
        self._iid = None

    def GetDVMStatus(self):
        """
        Get current status of selected virtual accelerator.

        :return: DVM status
        :rtype: DVMStatus
        :raises RuntimeError: if the exit code indicates any error
        """
        status = Int()
        self._call('GetDVMStatus', self.iid, status)
        return DVMStatus(status.value)

    def SelectVAcc(self, vaccnum):
        """
        Select the virtual accelerator.

        :param int vaccnum: virtual accelerator number (0-255)
        :raises RuntimeError: if the exit code indicates any error
        """
        self._call('SelectVAcc', self.iid, Int(vaccnum))
        self._selected_vacc = vaccnum

    def SelectMEFI(self, vaccnum, energy, focus, intensity, gantry_angle=0):
        """
        Select EFI combination for the currently selected VAcc.

        :param int vaccnum: virtual accelerator number (0-255)
        :param int energy: energy channel (1-255)
        :param int focus: focus channel (1-6)
        :param int intensity: intensity channel (1-15)
        :param int gantry_angle: gantry angle index (1-36)
        :return: physical EFI values
        :rtype: EFI
        :raises RuntimeError: if the exit code indicates any error

        CAUTION: SelectVAcc must be called before invoking this function!
        """
        values = [Double(), Double(), Double(), Double()]
        self._call('SelectMEFI', self.iid, Int(vaccnum),
                   Int(energy), Int(focus), Int(intensity), Int(gantry_angle),
                   *values)
        if vaccnum == self._selected_vacc:
            self._selected_efi = EFI(energy, focus, intensity, gantry_angle)
        else:
            self._logger.warn('You must call SelectVAcc() before SelectMEFI()!')
        return EFI(*[v.value for v in values])

    def GetSelectedVAcc(self):
        """
        Get selected virtual accelerator.

        :return: virtual accelerator number (0-255)
        :rtype: int
        :raises RuntimeError: if the exit code indicates any error
        """
        vaccnum = Int()
        self._call('GetSelectedVAcc', self.iid, vaccnum)
        return vaccnum.value

    def GetFloatValue(self, name, options=GetOptions.Current):
        """
        Get parameter value.

        :param str name: parameter name
        :param GetOptions options: options
        :return: parameter value
        :rtype: float
        :raises RuntimeError: if the exit code indicates any error
        """
        value = Double()
        self._call('GetFloatValue', self.iid, Str(name), value, Int(options))
        return value.value

    def SetFloatValue(self, name, value, options=0):
        """
        Set parameter value.

        :param str name: parameter name
        :param float value: parameter value
        :param options: not used currently
        :raises RuntimeError: if the exit code indicates any error

        Changes take effect after calling :func:`ExecuteChanges`.
        """
        self._call('SetFloatValue', self.iid, Str(name), Double(value), Int(options))

    def ExecuteChanges(self, options):
        """
        Apply parameter changes.

        :param ExecOptions options: what to do exactly
        :raises RuntimeError: if the exit code indicates any error
        """
        self._call('ExecuteChanges', self.iid, Int(options))

    def SetNewValueCallback(self, callback):
        """Call SetNewValueCallback(). Not implemented!"""
        # TODO: docs do not specify when this is actually called
        # TODO: howto create a python callback? Use Cython?
        raise NotImplementedError()

    def GetFloatValueSD(self, name, options=0):
        """
        Get current beam measurement at specific element.

        :param str name: parameter name (<observable>_<element name>)
        :param GetSDOptions options: options
        :return: measured value
        :rtype: float
        :raises RuntimeError: if the exit code indicates any error
        """
        value = Double()
        self._call('GetFloatValueSD', self.iid, Str(name), value, Int(options))
        return value.value

    def GetLastFloatValueSD(self, name, vaccnum,
                            energy, focus, intensity, gantry_angle=0,
                            options=0):
        """
        Get previous beam measurement at specific element.

        :param str name: parameter name (<observable>_<element name>)
        :param int vaccnum: virtual accelerator number (0-255)
        :param GetSDOptions options: options
        :return: measured value and EFI combination
        :rtype: tuple
        :raises RuntimeError: if the exit code indicates any error
        """
        value = Double()
        self._call('GetLastFloatValueSD', self.iid, Str(name),
                   value, Int(vaccnum), Int(options),
                   Int(energy), Int(focus), Int(intensity), Int(gantry_angle))
        return value.value

    def StartRampDataGeneration(self, vaccnum, energy, focus, intensity):
        """
        Call StartRampDataGeneration().
        """
        order_num = Int()
        self._call('StartRampDataGeneration', self.iid,
                   Int(vaccnum), Int(energy), Int(focus), Int(intensity),
                   order_num)
        sel_efi = self._selected_efi
        if (vaccnum != self._selected_vacc or
            energy != sel_efi.energy or
            focus != sel_efi.focus or
            intensity != sel_efi.intensity):
            self._logger.warn("You must call SelectEFI() before StartRampDataGeneration()!")
        return order_num.value

    def GetRampDataValue(self, order_num, event_num, delay,
                         parameter_name, device_name):
        """
        Call GetRampDataValue()
        """
        value = Double()
        self._call('GetRampDataValue', self.iid,
                   Int(order_num), Int(event_num), Int(delay),
                   Str(parameter_name), Str(device_name),
                   value)
        return value.value

    def SetIPC_DVM_ID(self, name):
        """Call SetIPC_DVM_ID(). Not implemented!"""
        raise NotImplementedError() # TODO

    def GetMEFIValue(self):
        """
        Retrieve EFI values for current selection.

        :return: physical EFI values, EFI channel numbers
        :rtype: tuple(EFI, EFI)
        :raises RuntimeError: if the exit code indicates any error
        """
        values = [Double(), Double(), Double(), Double()]
        channels = [Int(), Int(), Int(), Int()]
        self._call('GetMEFIValue', self.iid, *(values + channels))
        return (EFI(*[v.value for v in values]),
                EFI(*[c.value for c in channels]))
