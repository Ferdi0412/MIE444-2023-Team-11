"""Decodes responses from the robot."""
######################
### BASE LIBRARIES ###
######################
import struct as _struct

########################
### CUSTOM LIBRARIES ###
########################
import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__))) ## Expose local modules

import connector._config as _config

_ = sys.path.pop()


##########################
### INTERNAL FUNCTIONS ###
##########################
def _decode_float(val: bytes) -> float:
    return float(val)

def _decode_int(val: bytes) -> int:
    return int(val)

def _decode_single_ultrasonic(val: bytes) -> tuple[str, float]:
    sensor_id, sensor_reading = val.decode('utf-8').split('_')
    return sensor_id, _decode_float(sensor_reading)

########################
### PUBLIC FUNCTIONS ###
########################
def decode_ultrasonics(msg: bytes) -> dict[str, float]:
    ## Ignore leading "U_", and any trailing '\n', '\r'
    msg_vals = msg[2:].replace(b'\n', b'').replace(b'\r', b'')
    vals = msg_vals.split(b';')
    return dict(_decode_single_ultrasonic(v) for v in vals)

def decode_progress(msg: bytes) -> float:
    ## Ignore leading "P_" and any trailing '\n' or '\r'
    msg_val = msg[2:].replace(b'\n', b'').replace(b'\r', b'')
    return _decode_float(msg_val)

