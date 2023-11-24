"""Encode messages going to the robot..."""
######################
### BASE LIBRARIES ###
######################
import struct as _struct

########################
### CUSTOM LIBRARIES ###
########################
import sys, os; sys.path.append(os.path.dirname(__file__)) ## Expose local modules

import robot_config as _config

_ = sys.path.pop() ## Cleanup local modules


##########################
### INTERNAL FUNCTIONS ###
##########################
def _encode_int(int_val: int) -> bytes:
    return _struct.pack('<h', int_val)



def _encode_float(float_val: float) -> bytes:
    return _struct.pack('<f', float_val)



def _encode_char(char_val: int) -> bytes:
    return (char_val).to_bytes(1, byteorder='little')
    # return chr(char_val).encode('utf-8')



#######################
### MOTOR FUNCTIONS ###
#######################
def encode_forward(dist: float, speed: float = 60.0) -> bytes:
    """Encodes a GO-FORWARD message to robot.

    PARAMS:
    |- dist <float>
    |      Distance to travel (in inches). If negative, robot will go backwards.
    |- [speed] <float>
    |      RPM of wheels.
    """
    ## Translate linear distance to pulses of motor, floor to ensure int value
    pulses_left:  int = int( ( dist * _config.PULSES_FWD * _config.MOTOR_LEFT_FACTOR  ) // 1)
    pulses_right: int = int( ( dist * _config.PULSES_FWD * _config.MOTOR_RIGHT_FACTOR ) // 1)

    ## Ensure speed does not exceed max speed
    speed = min( abs(speed), _config.MOTOR_SPEED_MAX )

    ## If distance is less than 1 (go backwards), speed should be less than 1
    if dist < 0:
        pulses_left  = abs(pulses_left)
        pulses_right = abs(pulses_right)
        speed *= -1

    ## msg consists of message to left & right motor, with number of pulses and speed to travel
    msg: bytes = b'M' + _config.MOTOR_LEFT  + _encode_int( pulses_left ) + _encode_float( speed * _config.MOTOR_LEFT_FACTOR  )\
               + b'M' + _config.MOTOR_RIGHT + _encode_int( pulses_right ) + _encode_float( speed * _config.MOTOR_RIGHT_FACTOR )

    ## Return formatted message
    return msg



def encode_rotate(angle: int, speed: float = 30.0) -> bytes:
    """Encodes a ROTATE-CLOCKWISE message to robot.

    PARAMS:
    |- angle <float>
    |       Angle to rotate (in degrees). If negative, robot rotates counter-clockwise.
    |- [speed] <float>
    |       RPM of wheels.
    """
    ## Translate rotational motion to pulses of motor, floor to ensure int value
    pulses_left:  int = int( ( angle * _config.PULSES_ROT * _config.MOTOR_LEFT_FACTOR  ) // 1)
    pulses_right: int = int( ( angle * _config.PULSES_ROT * _config.MOTOR_RIGHT_FACTOR ) // 1)

    ## Ensure speed does not exceed max speed
    speed = min( abs(speed), _config.MOTOR_SPEED_MAX )

    ## If distance is less than 1 (counter-clockwise), negate speed
    if angle < 0:
        pulses_left  = abs(pulses_left)
        pulses_right = abs(pulses_right)
        speed  *= -1

    ## Message to each motor, with number of pulses to travel. If clockwise, right motor is negative direction.
    msg: bytes = b'M' + _config.MOTOR_LEFT  + _encode_int( pulses_left  ) + _encode_float(  speed * _config.MOTOR_LEFT_FACTOR  )\
               + b'M' + _config.MOTOR_RIGHT + _encode_int( pulses_right ) + _encode_float( -speed * _config.MOTOR_RIGHT_FACTOR )

    ## Return formatted message
    return msg



def encode_stop() -> bytes:
    """Encode a message to force robot to stop latest motion."""
    return b'S'



def encode_progress() -> bytes:
    """Encode a message to request each motor's progress on latest movement command."""
    return b'P' + _config.MOTOR_LEFT\
         + b'P' + _config.MOTOR_RIGHT



def encode_active() -> bytes:
    """Encode message to request each motor's active state."""
    return b'A' + _config.MOTOR_LEFT\
         + b'A' + _config.MOTOR_RIGHT



############################
### AUXILLIARY FUNCTIONS ###
############################
def encode_ultrasonics() -> bytes:
    """Encode a message to request the Ultrasonic readings."""
    return b'U'



def encode_led(r: int, g: int, b: int) -> bytes:
    """Encode a message to set the LED color."""
    ## All values must be positive, and in [0, 255]
    r = min(abs(r), 255)
    g = min(abs(g), 255)
    b = min(abs(b), 255)

    ## One message to set each colour
    msg = b'L' + _encode_char(r) + _encode_char(g) + _encode_char(b)

    ## Return formatted message
    return msg



def encode_motor_name() -> bytes:
    """Triggers Sensor board to send names to each Motor board."""
    return b'X'
