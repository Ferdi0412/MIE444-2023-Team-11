"""Encode messages going to the robot..."""
######################
### BASE LIBRARIES ###
######################
import struct as _struct

########################
### CUSTOM LIBRARIES ###
########################
import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__))) ## Expose local modules

import connector._config as _config

# _ = sys.path.pop() ## Cleanup local modules


##########################
### INTERNAL FUNCTIONS ###
##########################
def _encode_int(int_val: int) -> bytes:
    return _struct.pack('<H', int(int_val))



def _encode_float(float_val: float) -> bytes:
    return _struct.pack('<f', float_val)



def _encode_char(char_val: int) -> bytes:
    return (char_val).to_bytes(1, byteorder='little')
    # return chr(char_val).encode('utf-8')



def _hex(val: int | str | bytes) -> int:
    """Translate hex input to an integer."""
    if isinstance(val, str | bytes):
        return ord(val)
    return val

########################
### PUBLIC FUNCTIONS ###
########################
def encode_forward(dist: float = None) -> bytes:
    return b"W" + ((_config.DATA_PREFIX + _encode_int(dist * _config.TIME_TO_DIST + _config.TIME_OFFSET)) if dist is not None else b"")

def encode_backwards(dist: float = None) -> bytes:
    return b"S" + ((_config.DATA_PREFIX + _encode_int(dist * _config.TIME_TO_DIST + _config.TIME_OFFSET)) if dist is not None else b"")

def encode_clockwise(angle: float = None) -> bytes:
    return b"E" + ((_config.DATA_PREFIX + _encode_int(angle * _config.TIME_TO_ANGLE + _config.TIME_ANGLE_OFFSET)) if angle is not None else b"")

def encode_counter_clockwise(angle: float) -> bytes:
    return b"Q" + ((_config.DATA_PREFIX + _encode_int(angle * _config.TIME_TO_ANGLE + _config.TIME_ANGLE_OFFSET)) if angle is not None else b"")

def encode_stop() -> bytes:
    return b"X"

def encode_gripper_close() -> bytes:
    return b"GC"

def encode_gripper_open() -> bytes:
    return b"GO"

def encode_gripper_lift() -> bytes:
    return b"GU"

def encode_gripper_lower() -> bytes:
    return b"GD"

def encode_led(r: int, g: int, b: int) -> bytes:
    return b"L" + _encode_char(_hex(r)) + _encode_char(_hex(g)) + _encode_char(_hex(b))

def encode_active() -> bytes:
    return b"A"

def encode_progress() -> bytes:
    return b"P"

def encode_ultrasonic() -> bytes:
    return b"U"
