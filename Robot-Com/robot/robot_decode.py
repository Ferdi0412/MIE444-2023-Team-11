"""Decode messages received from the robot..."""
_CM_TO_IN = 0.393701

######################
### BASE LIBRARIES ###
######################
import struct as _struct
# import enum   as _enum

########################
### CUSTOM LIBRARIES ###
########################
import sys, os; sys.path.append(os.path.dirname(__file__)) ## Expose local modules

import config as _config

_ = sys.path.pop() ## Cleanup local modules

##################
### ENUM CLASS ###
##################
class Message:
    """Pseudo-enum...

    Can check if message is of type using:

    msg = serial.Serial(COM).readline()
    print("Match!" if msg[0] == Message.MOVE else "Try again...")
    """
    MOVE       = b'M'[0]
    PROGRESS   = b'P'[0]
    STOP       = b'S'[0]
    ACTIVE     = b'A'[0]
    ULTRASONIC = b'U'[0]

##########################
### INTERNAL FUNCTIONS ###
##########################
def _decode_int(int_val: bytes) -> int:
    # print(int_val)
    return _struct.unpack('<h', int_val)[0]

def _decode_float(float_val: bytes) -> bytes:
    # print(float_val)
    return _struct.unpack('<f', float_val)[0]

## Indexing bytes_element[i] will return an int type...
# def _encode_char(char_val: int) -> bytes:
#     return char_val

## Generic function used to decode several request responses
def _decode_progress(msg: bytes) -> tuple[bytes, float]:
    """Returns tuple containing motor_id and motor_progress.
    motor_progress is in inches, under assumption progress on rotate is never needed.
    """
    ## Extract each field from message
    # msg_type       = msg[0:1]
    motor_id       = msg[ 1 : 2 ]
    motor_progress = msg[ 2 : ( 2 + _config.SIZEOF_INT ) ]

    ## Check that motor_progress is long enough
    # assert( motor_progress == _config.SIZEOF_FLOAT )

    ## Decode motor_progress
    motor_progress = _decode_int(motor_progress)

    ## Convert from pulses to inches of linear motion
    motor_progress /= _config.PULSES_FWD

    ## Return tuple of [motor_id, motor_progress,]
    return motor_id, motor_progress

#######################
### MOTOR FUNCTIONS ###
#######################
def decode_move(msg: bytes) -> tuple[bytes, float]:
    """Decode response to a MOVE request."""
    return _decode_progress(msg)

def decode_progress(msg: bytes) -> tuple[bytes, float]:
    """Decode response to a PROGRESS request."""
    return _decode_progress(msg)

def decode_stop(msg: bytes) -> tuple[bytes, float]:
    """Decode response to a STOP request."""
    return _decode_progress(msg)

def decode_active(msg: bytes) -> tuple[bytes, bool]:
    """Decode response to an ACTIVE request."""
    motor_id  = msg[ 1 : 2 ]
    ## not, as I accidentally put to return target_speed == 0 on arduinos...
    is_active = not msg[ 2 ]
    return motor_id, is_active

############################
### AUXILLIARY FUNCTIONS ###
############################
def decode_ultrasonic(msg: bytes) -> list[float]:
    """Decodes response to an ULTRASONIC request."""
    ## Drop b'U' at start...
    msg = msg[1:]
    val_counts = len(msg) // _config.SIZEOF_INT

    ## LIST-COMPREHESION, to make less readable ;) -> For equivalent for loop, see below
    readings = [ _decode_int( msg[ (_config.SIZEOF_INT * i) : (_config.SIZEOF_INT * (i + 1) ) ] ) * _CM_TO_IN
                 for i in range(val_counts)]

    return readings

    ## EQUIVALENT TO THE ABOVE LIST-COMPREHENSION:
    # vals = []
    # for i in range(val_counts):
    #     ## Get bytes for a single value from msg
    #     val = msg[ ( _config.SIZEOF_INT * i ) : ( _config.SIZEOF_INT * (i + 1) + 1) ]

    #     ## Decode value, and convert from cm (robot uses cm) to inch (for automation code)
    #     val = _decode_int(val) * _CM_TO_IN

    #     ## Append val
    #     vals.append(val)
