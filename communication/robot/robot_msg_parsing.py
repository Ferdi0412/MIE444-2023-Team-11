"""Functions to handle messages from Robot according to API.

"""
from typing import Tuple, Dict

##################
###   CUSTOM   ###
### LIBRARIES  ###
##################
## == Expose them ==
import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))

## == Import them ==
from communication.serial_base import decode_float, decode_int16, decode_int32, decode_char

## == Cleanup ==
sys.path.pop()



#################
###  PARSING  ###
### FUNCTIONS ###
#################
def is_motor_ack(msg: bytes) -> bool:
    """Returns True if message is of type motor_ack."""
    return msg[0:1] == b'M'

def parse_motor_ack(msg: bytes) -> Tuple[bytes, float]:
    """Unpack/parse motor acknowledge movement.

    RETURNS:
    |- 1: motor_id <bytes>
    |      This is the id of the motor that acknowledged the message.
    |- 2: last_pos <float>
    |      This is the progress along the latest move of the motor.
    """
    motor_id = msg[1:2]
    last_pos = decode_float(msg[2:6])[0]
    return motor_id, last_pos



def is_motor_stop_ack(msg: bytes) -> bool:
    """Returns True if message is of type motor_stop_ack."""
    return msg[0:1] == b'S'

def parse_motor_stop_ack(msg: bytes) -> Tuple[bytes, float]:
    """Unpack/parse motor STOP acknowledge movement.

    RETURNS:
    |- 1: motor_id <bytes>
    |      This is the id of the motor that acknowledged the message.
    |- 2: last_pos <float>
    |      This is the progress along the latest move of the motor.
    """
    motor_id = msg[1:2]
    last_pos = decode_float(msg[2:6])[0]
    return motor_id, last_pos



def is_motor_active_msg(msg: bytes) -> bool:
    """Returns True if message is of type motor_moving."""
    return msg[0:1] == b'A'

def parse_motor_active(msg: bytes) -> Tuple[bytes, bool]:
    """Unpacks/parses motor moving state message.

    RETURNS:
    |- 1: motor_id <bytes>
    |- 2: is_active <bool>
    """
    motor_id  = msg[1:2]
    is_active = bool(decode_char(msg[2])[0])
    return motor_id, is_active



def is_motor_pos_msg(msg: bytes) -> bool:
    """Returns True if message is of type motor_pos."""
    return msg[0:1] == b'P'

def parse_motor_pos(msg: bytes) -> Tuple[bytes, float]:
    """Unpack/parse the position of a motor.

    RETURNS:
    |- 1: motor_id <bytes>
    |- 2: motor_pos <float>
    """
    motor_id  = msg[1:2]
    motor_pos = decode_float(msg[2:6])[0]
    return motor_id, motor_pos



def is_ultrasonic(msg: bytes) -> bool:
    """Returns True if message is an ultrasonics message from the robot."""
    return msg[0:1] == b'U'

def parse_ultrasonics(msg: bytes) -> Dict[bytes, float]:
    """Unpack/parse the readings from the ultrasonic sensors.
    Returns <dict> where keys are ultrasonic sensor IDs, and values are most recent readings.
    """
    ## Length of a message is 5 (1 byte for ID, 4 for float value).
    us_count = len(msg[1:]) // 5
    readings = {}
    for i in range(us_count):
        ## Get index of first and last bytes corresponding to a given sensor
        start = i * 4 + 1
        end   = (i + 1) * 4 + 1
        ## Get ID and reading of sensor
        sensor_id = us_count[start:start+1]
        reading   = decode_float( msg[start+1:end] )[0]
        ## Add to dictionary of readings
        readings[ sensor_id ] = reading
    return readings



def is_gyroscope(msg: bytes) -> bool:
    """Returns True if message is a gyroscope message from the robot."""
    return msg[0:1] == 'G'

def parse_gyroscope(msg: bytes) -> Dict[bytes, float]:
    """Unpacks/parses readings from gyroscope.
    Reutrns <dict> where keys are direction/metric, and values are the most recent readings.
    """
    ## Length of a message is 5 (1 byte for ID, 4 for float value).
    us_count = len(msg[1:]) // 5
    readings = {}
    for i in range(us_count):
        ## Get index of first and last bytes corresponding to a given value from sensor
        start = i * 4 + 1
        end   = (i + 1) * 4 + 1
        ## Get ID of measurement, and newest reading
        sensor_id = us_count[start:start+1]
        reading   = decode_float( msg[start+1:end] )[0]
        ## Add to dictionary of readings
        readings[ sensor_id ] = reading
    return readings
