"""Functions to work with serial communication.

Note: For unpacking stuff, no assumptions about endianess are made...

Requires pyserial library...

"""

import serial
from threading import Thread
import struct
import typing

def setup_serial(port: str, timeout: float = None):
    """

    PARAMS:
    |- port <str>:
    |    Port to connect to, eg "COM5".
    |- [timeout] <float>:
    |    Seconds for timeout. If this is given, methods such as Serial.read() is no longer blocking, and will
    |    return after this many seconds. If timeout occurs, an empty <bytes> is returned from the .read() call.
    |    [default] -> <None>; Blocking behaviour.
    """
    return serial.Serial(port, timeout=timeout)

def decode_int16(value: bytes, unsigned: bool = False) -> typing.Tuple[int]:
    """Unpack/decode int_16_t ("short") values.

    Unpacks a series of serialized (ie. byte-encoded) int16 values into a tuple of ints.

    PARAMS:
    |- value <bytes>:
    |    Value to unpack.
    |- [unsigned] <bool>:
    |    If true(thy), will interpret value as an unsigned int_16_t, otherwise will interpret as signed.
    |    [default] -> False; Interprets Signed.
    """
    return struct.unpack('H' if unsigned else 'h', value)

def decode_int32(value: bytes, unsigned: bool = False) -> typing.Tuple[int]:
    """Unpack/decode int_32_t ("int") values.

    Unpacks a series of serialized (ie. byte-encoded) int32 values into a tuple of ints.

    PARAMS:
    |- value <bytes>:
    |    Value to unpack.
    |- [unsigned] <bool>:
    |    If true(thy), will interpret value as an unsigned int_32_t, otherwise will interpret as signed.
    |    [default] -> False; Interprets Signed.
    """
    return struct.unpack('I' if unsigned else 'i', value)

def decode_float(value: bytes) -> typing.Tuple[float]:
    """Unpack/decode float values.

    Unpacks a series of serialized (ie. byte-encoded) float values into a tuple of floats.

    PARAMS:
    |- value <bytes>:
    |    Value to unpack.
    """
    return struct.unpack('f', value)
