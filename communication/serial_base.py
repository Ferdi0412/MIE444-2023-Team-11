"""Functions to work with serial communication.

Note: For unpacking stuff, no assumptions about endianess are made...

Requires pyserial library...

"""

from serial    import Serial
from struct    import unpack, pack
from typing    import Tuple

ENDIANESS = '>'

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
    return Serial(port, timeout=timeout)



def decode_int16(value: bytes, *, unsigned: bool = False) -> Tuple[int]:
    """Returns tuple of all int16_t (short) stored as bytes in msg.

    PARAMS:
    |- msg <bytes>:
    |     Bytes/string to decode int16_t (short) values from.
    |     All sets ofbytes in msg should correspond to instances of this type.
    |- [unsigned] <bool>:
    |     If true, msg is interpreted as uint16_t.
    |     Otherwise interpreted as int16_t.
    """
    return unpack(ENDIANESS + ('H' if unsigned else 'h'), value)

def encode_int16(value: int, *, unsigned: bool = False) -> bytes:
    """Returns value encoded as bytes representing an int16_t (short) value, to send via. Serial.

    PARAMS:
    |- value <int>:
    |     Value to encode as bytes.
    |- [unsigned] <bool>:
    |     If True, will encode as uint16_t.
    |     Otherwise will encode as int16_t.
    """
    return pack(ENDIANESS + ('H' if unsigned else 'h'), value)



def decode_int32(value: bytes, *, unsigned: bool = False) -> Tuple[int]:
    """Returns tuple of all int32_t (int) stored as bytes in msg.

    PARAMS:
    |- msg <bytes>:
    |     Bytes/string to decode int32_t (int) values from.
    |     All sets ofbytes in msg should correspond to instances of this type.
    |- [unsigned] <bool>:
    |     If true, msg is interpreted as uint32_t.
    |     Otherwise interpreted as int32_t.
    """
    return unpack(ENDIANESS + ('I' if unsigned else 'i'), value)

def encode_int32(value: int, *, unsigned: bool = False) -> bytes:
    """Returns value encoded as bytes representing an int32_t (int) value, to send via. Serial.

    PARAMS:
    |- value <int>:
    |     Value to encode as bytes.
    |- [unsigned] <bool>:
    |     If True, will encode as uint32_t.
    |     Otherwise will encode as int32_t.
    """
    return pack(ENDIANESS + ('I' if unsigned else 'i'), value)



def decode_char(value: bytes, *, unsigned: bool = False) -> Tuple[int]:
    """Returns tuple of all char stored as bytes in msg.

    PARAMS:
    |- msg <bytes>:
    |     Bytes/string to decode char values from.
    |     All sets of bytes in msg should correspond to instances of this type.
    |- [unsigned] <bool>:
    |     If true, msg is interpreted as unsigned char.
    |     Otherwise interpreted as signed char.
    """
    return unpack(ENDIANESS + ('B' if unsigned else 'b'), value)

def encode_char(value: int, *, unsigned: bool = False) -> bytes:
    """Returns value encoded as bytes representing a char value, to send via. Serial.

    PARAMS:
    |- value <int>:
    |     Value to encode as bytes.
    |- [unsigned] <bool>:
    |     If True, will encode as unsigned char.
    |     Otherwise will encode as signed char.
    """
    return pack(ENDIANESS + ('B' if unsigned else 'b'), value)



def decode_float(value: bytes) -> Tuple[float]:
    """Returns tuple of all floats stored as bytes in msg.

    PARAMS:
    |- msg <bytes>:
    |     Bytes/string to decode float values from.
    |     All sets ofbytes in msg should correspond to instances of this type.
    """
    return unpack('f', value)

def encode_float(value: float) -> bytes:
    """Returns bytes represengint the float value given.

    PARAMS:
    |- value <float>:
    |     Value to encode as 4 bytes representing a float.
    """
    return pack('f', value)
