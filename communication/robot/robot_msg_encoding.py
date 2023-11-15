"""Functions to format messages to send to Robot accodring to API.

"""
from typing import Tuple, Dict

##################
###   CUSTOM   ###
### LIBRARIES  ###
##################
## == Expose them ==
import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))

## == Import them ==
from communication.serial_base import encode_float, encode_int16, encode_int32, encode_char

## == Cleanup ==
sys.path.pop()



##################
###  ENCODING  ###
### FUNCTIONS  ###
##################
def encode_motor_set(motor_id: bytes, motor_pos: float, motor_speed: float) -> bytes:
    """Encode 'M' message."""
    msg = bytearray(b'M')
    msg.append(motor_id)
    msg.extend(encode_float(motor_pos))
    msg.extend(encode_float(motor_speed))
    return bytes(msg)

def encode_motor_stop(motor_id: bytes) -> bytes:
    """Encode 'S' message."""
    return b'S'

def encode_pos(motor_id: bytes) -> bytes:
    """Encode 'P' message."""
    msg = bytearray(b'P')
    msg.append(motor_id)
    return bytes(msg)

def encode_active(motor_id: bytes) -> bytes:
    """Encode 'A' message."""
    msg = bytearray(b'A')
    msg.append(motor_id)
    return bytes(msg)

def encode_led(state: bool) -> bytes:
    msg = bytearray(b'L')
    msg.append(encode_char(int(state)))
    return bytes(msg)

def encode_ultrasonic() -> bytes:
    return b'U'

def encode_gyroscope() -> bytes:
    return b'G'
