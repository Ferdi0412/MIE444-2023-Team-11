"""Built on top of serial_class.Serial, to expose functions specific to our robot.

This will format and handle messages sent to-and-from robot.

NOTE: All byte_i are offset by 1, as first byte is actually always the API character (eg. b'M' for MOVE).

=== API => To Robot ===
|=> MOVE <CMD>
| 'M' {byte_0: MOTOR_ID <0: FL, 1: FR, 2: BL, 3: BR>
|      byte_1_4: Target_Pos
|      byte_5_8: Target_Speed}

|=> STOP <CMD>
| 'S' {byte_0: MOTOR_ID}

|=> PROGRESS
| 'P' {byte_0: MOTOR_ID}

|=> ACTIVE
| 'A' {byte_0: MOTOR_ID}

|=> LED
| 'L' {byte_0: STATE}

|=> ULTRASONICS
| 'U' {void}


=== API => From Robot ===
|=> MOTOR
| 'M' {byte_0: MOTOR_ID
|      byte_1_4: Progress}

|=> STOP
| 'S' {byte_0: MOTOR_ID
       byte_1_4: Progress}

|=> PROGRESS
| 'P' {byte_0: MOTOR_ID
       byte_1_4: Progress}

|=> ACTIVE
| 'A' {byte_0: MOTOR_ID
       byte_1_4: State}

|=> ULTRASONICS <Planned 6 of them>
| 'U' {byte_0_4:   US_0 <FL>, FLOAT
       byte_5_9:   US_1 <FR>, FLOAT
       byte_10_14: US_2 <R>, FLOAT
       byte_15_18: US_3 <B>, FLOAT
       byte_19_24: US_4 <L>, FLOAT
       byte_25_28: US_5 <Gripper>, FLOAT}
"""
from typing import Tuple, Dict
from math import cos, sin, atan, pi

import sys, os;

##################
###   CUSTOM   ###
### LIBRARIES  ###
##################
## 1) General
## == Expose them ==
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

## == Import them ==
from communication.serial_class  import NewSerial, MaxRetries
from communication.serial_base   import decode_float#, decode_char, decode_int16, decode_int32

## == Cleanup ==
sys.path.pop()

## 2) Our robot-specific
## == Expose them ==
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

## == Import them ==
from robot.robot_msg_encoding import encode_motor_set, encode_led# , encode_motor_stop, encode_active, encode_pos
from robot_msg_parsing        import is_ultrasonic, parse_ultrasonics

## == Cleanup ==
sys.path.pop()



##################
###   CONFIG   ###
##################
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
ULTRASONICS  = [b'\x00', b'\x01', b'\x02', b'\x03', b'\x04']
MOTORS       = [b'\x01', b'\x02', b'\x03', b'\x04'] ## Each ID must be no more than 1 byte long....

###################
### API RELATED ###
###################
def decode_motor_reply(msg: bytes) -> Tuple[bytes, float]:
    """Returns motor response (always motor_id followed by progress)."""
    motor_id       = msg[1:2]
    motor_progress = decode_float(msg[2:6])[0]
    return motor_id, motor_progress


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
    msg.extend(encode_motor_set(b'1', pos_fl_br, speed_fl_br)) # fl := 1
    msg.extend(encode_motor_set(b'2', pos_fr_bl, speed_fr_bl)) # fr := 2
    msg.extend(encode_motor_set(b'3', pos_fr_bl, speed_fr_bl)) # bl := 3
    msg.extend(encode_motor_set(b'4', pos_fl_br, speed_fl_br)) # br := 4
    return bytes(msg)

def encode_rotate(clockwise_angle: float, *, speed: float = ROTATE_SPEED) -> bytes:
    """Encode rotation command to send to machine."""
    pulses = clockwise_angle * PPT / 360
    msg = bytearray()
    msg.extend(encode_motor_set(b'1',  pulses, speed)) # fl := 1
    msg.extend(encode_motor_set(b'2', -pulses, speed)) # fr := 2
    msg.extend(encode_motor_set(b'3',  pulses, speed)) # bl := 3
    msg.extend(encode_motor_set(b'4', -pulses, speed)) # br := 4
    return bytes(msg)



##############################
### MOTOR RESPONSE CHECKER ###
##############################
class MotorResponseCheck (set):
    """Class that can be passed to check that all motors are returned.

    Set[bytes]
    """

    def __init__(self, api_id: bytes):
        """Allow a set to be built using only the first byte to assign for each value in the set."""
        super().__init__( api_id + motor[0:1] for motor in MOTORS )

    def __call__(self, msg: bytes):
        """Allow class instance to be called like a function."""
        return msg[0:2] in self

    def remove(self, msg: bytes):
        """Allow user to remove instance, using an input of undefined length."""
        return super().remove( msg[0:2] )



#####################
### WRAPPER CLASS ###
#####################
class Robot (NewSerial):
    """
    """
    def _motor_msg(self, api_id: bytes, msg: bytes, *, silence_error: bool = False):
        ## Dictionary to keep track of response values
        progress = {mid: None for mid in MOTORS}

        ## Checker to ensure response from each motor
        motor_checker = MotorResponseCheck(api_id)

        self.send(msg)

        try:
            for _ in range(len(motor_checker)):
                reply = self.blocking_recv(motor_checker)

                ## Decode reply
                motor_id, motor_prog = decode_motor_reply(reply)
                progress[motor_id]   = motor_prog

                ## Remove motor from list of motors
                motor_checker.remove(motor_id)

        ## If MaxRetries raise whilst any motor reply is still missing...
        except MaxRetries as exc:
            ## If silence_error, return with None(s) where missing motors are...
            if silence_error:
                return progress
            missing_motors = ', '.join(str(mid) for mid in motor_checker)
            raise MaxRetries(f"Never received confirmation from motors: [{missing_motors}]") from exc

        return progress


    ## TODO: Update functions to re-direct non-move function to include motor_id??? Or maybe not???
    def move(self, fwd: float, right: float, *, speed: float = BASE_SPEED, silence_error: bool = False) -> Dict[bytes, float]:
        """Send movement command via. Serial connection."""
        msg = encode_move(fwd, right, speed = speed)
        return self._motor_msg(b'M', msg, silence_error=silence_error)

    def rotate(self, angle: float, *, silence_error: bool = False) -> Dict[bytes, float]:
        """Send rotate command via. Serial connection."""
        msg = encode_rotate(angle)
        return self._motor_msg(b'M', msg, silence_error=silence_error)


    def stop(self, *, silence_error: bool = False) -> Dict[bytes, float]:
        """Sends stop command via. Serial connection."""
        return self._motor_msg(b'S', b'S', silence_error=silence_error)


    def progress(self, *, silence_error: bool = False) -> Dict[bytes, float]:
        """"""
        return self._motor_msg(b'P', b'P', silence_error=silence_error)


    def active(self, *, silence_error: bool = False) -> Dict[bytes, float]:
        """"""
        return self._motor_msg(b'A', b'A', silence_error=silence_error)


    def get_ultrasonic_readings(self, *, assert_all_ids: bool = True) -> Dict[bytes, float]:
        """Returns dict of ultrasonic readings.

        PARAMS:
        |- [assert_all_ids = default True]:
        |     Asserts that all ultrasonic_ids are in the response if (and only if) this is True.
        |     To catch, use 'try: ...; except AssertionError as exc: ...;
        """
        msg = self.send_recv(b'U', is_ultrasonic)
        returned_values = parse_ultrasonics(msg)

        ## If assert_all_ids check that all values contained in response message
        if assert_all_ids:
            assert all(usid in returned_values.keys() for usid in ULTRASONICS)

        return returned_values

    def led(self, state: bool) -> None:
        """Turn LED on/off."""
        self.send(encode_led(state))
