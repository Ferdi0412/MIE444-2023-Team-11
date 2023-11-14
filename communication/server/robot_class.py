"""Built on top of serial_class.Serial, to expose functions specific to our robot."""
from typing import Tuple, Dict
from math import cos, sin, atan, pi

import sys, os; sys.path.append(os.path.dirname(__file__))

from ..serial_class import Serial
import robot_msg_encoding as enc

## Motor IDs:
## Front left  := 1
## Front right := 2
## Back left   := 3
## Back right  := 4

WHEEL_DIAM   = 1
PPR          = 420 # Pulses per revolution
FWD_TO_SIDE  = 1.7
BASE_SPEED   = 25
PPT          = 420 # Pulses per turn of robot
ROTATE_SPEED = 15

###################
### API RELATED ###
###################
def get_fwd_pulses(fwd_dist: float) -> float:
    """Translates forwards distance in inches to encoder pulses.

    Forward distance in inches divided by perimeter of wheel is number of rotations required.
    Number of rotations times pulses per revolution is number of pulses required to travel distance.
    """
    num_rot = fwd_dist / (2 * pi * WHEEL_DIAM)
    return num_rot * PPR

def get_right_pulses(right_dist: float) -> float:
    """Translates sideways distance in inches to encoder pulses."""
    return get_fwd_pulses(right_dist) * FWD_TO_SIDE

######################
### HIGH-LEVEL API ###
######################
def encode_move(fwd_dist: float, right_dist: float, *, speed: float = BASE_SPEED) -> bytes:
    """Encode movement command to what will be sent to machine."""
    ## Calculate pulses for purely forward
    fwd_pos   = get_fwd_pulses(fwd_dist)
    ## Calculate pulses for purely right
    right_pos = get_right_pulses(right_dist)
    ## Calculate pulses on front left and back right; front right back left; respectively
    pos_fl_br = fwd_pos + right_pos
    pos_fr_bl = fwd_pos - right_pos
    ## Calculate speed factor on fl_br and fr_bl respectively
    ## This is to ensure fl_br and fr_bl reach their target positions at the same time (take as long to travel)
    speed_fl_br = speed if (pos_fl_br > pos_fr_bl) else speed * (pos_fl_br / pos_fr_bl)
    speed_fr_bl = speed if (pos_fr_bl > pos_fl_br) else speed * (pos_fr_bl / pos_fl_br)

    ## Format message(s) for motors
    msg = bytearray()
    msg.extend(enc.encode_motor_set(b'1', pos_fl_br, speed_fl_br)) # fl := 1
    msg.extend(enc.encode_motor_set(b'2', pos_fr_bl, speed_fr_bl)) # fr := 2
    msg.extend(enc.encode_motor_set(b'3', pos_fr_bl, speed_fr_bl)) # bl := 3
    msg.extend(enc.encode_motor_set(b'4', pos_fl_br, speed_fl_br)) # br := 4
    return bytes(msg)

def encode_rotate(clockwise_angle: float, *, speed: float = ROTATE_SPEED) -> bytes:
    """Encode rotation command to send to machine."""
    pulses = clockwise_angle * PPT / 360
    msg = bytearray()
    msg.extend(enc.encode_motor_set(b'1',  pulses, speed)) # fl := 1
    msg.extend(enc.encode_motor_set(b'2', -pulses, speed)) # fr := 2
    msg.extend(enc.encode_motor_set(b'3',  pulses, speed)) # bl := 3
    msg.extend(enc.encode_motor_set(b'4', -pulses, speed)) # br := 4
    return bytes(msg)


#####################
### WRAPPER CLASS ###
#####################
class Robot (Serial):
    """

    FIELDS:
    |- motor_speed_factor <dict>
    |      Stores identifiers for motors and speed factors for them (ie. to calibrate their speeds).
    |
    |- base_speed <float>
    |      The nominal speed that the robot should apply in forward direction.
    |
    |- side_speed_factor <float>
    |      The ratio of side-ways speed to forward speed to apply.
    """

    def handle_request(header: bytes, msg: bytes) -> bytes:
        """Handle incoming request."""
        #match(header):
        pass


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.motor_speed_factor: Dict[bytes, float] = {}
    #     self.base_speed: float = 25
    #     self.side_speed_factor: float = 0.3
