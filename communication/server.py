from threading import Thread

import sys, os
sys.path.append(os.path.dirname(__file__))

from robot_comm  import Robot
from zmq_setup   import get_publisher, get_server
from serial_comm import setup_serial

##############
### CONFIG ###
##############
COM_OUT     = "COM13"
COM_IN      = "COM12"
ROB_TIMEOUT = 0.5

MAX_RETRIES = 20

## current_state's keys should never change...
current_state = {

}

#############
### SETUP ###
#############
publisher  = get_publisher()
server     = get_server()

## Non-blocking response connection, in order to use for publisher and individual command responses...
robot_cmd  = setup_serial(COM_OUT, ROB_TIMEOUT)
robot_resp = setup_serial(COM_IN,  ROB_TIMEOUT)

robot = Robot(robot_cmd, robot_resp)

class Unimplemented (Exception):
    pass

######################
### ASYNC MESSAGES ###
######################
def async_messages(msg: bytes) -> None:
    """This is called from a seperate thread that keeps reading messages from the robot when nothing else is happening..."""
    raise Unimplemented
    current_state.update(dict("Add something..."))
    publisher.send(bytes("Encode data here!!!"))

######################
### MESSAGE HANDLE ###
######################
def is_motor_ack(message: bytes) -> bool:
    """Returns True if message is of type motor_ack."""
    raise Unimplemented

def parse_motor_ack(message: bytes) -> dict | bool:
    """Unpack/parse motor acknowledge movement.

    RETURNS:
    |- <dict>:
    |     Undetermined keys, values describe errors.
    |- <bool>:
    |     True indicates acknowledge successful movement. False is indescript error.
    """
    raise Unimplemented

def parse_motor_moving(message: bytes) -> bool:
    """Unpacks/parses motor moving state message."""
    raise Unimplemented

def parse_motor_pos(message: bytes) -> float:
    """Unpack/parse the position of a motor."""
    raise Unimplemented

def is_ultrasonic(message: bytes) -> bool:
    """Returns True if message is an ultrasonics message from the robot."""
    raise Unimplemented

def parse_ultrasonics(message: bytes) -> dict:
    """Unpack/parse the readings from the ultrasonic sensors.
    Returns <dict> where keys are ultrasonic sensor IDs, and values are most recent readings.
    """
    raise Unimplemented

def is_gyroscope(message: bytes) -> bool:
    """Returns True if message is a gyroscope message from the robot."""
    raise Unimplemented

def parse_gyroscope(message: bytes) -> dict:
    """Unpacks/parses readings from gyroscope.
    Reutrns <dict> where keys are direction/metric, and values are the most recent readings.
    """
    raise Unimplemented



#####################
### SEND MESSAGES ###
#####################
def move(fwd: float, right: float) -> bool:
    """Send move command. Returns True if successful movement. Negative values indicate opposite direction."""
    raise Unimplemented
    ## TODO: Check encoding
    msg = b'{fwd}//{right}'
    return parse_motor_ack(robot.send_recv(msg, is_motor_ack))

def rotate(clockwise: float) -> bool:
    """Sends move command. Returns True if successful movement. Negative value is counter-clockwise."""
    raise Unimplemented
    msg = b''
    return parse_motor_ack(robot.send_recv(msg, is_motor_ack))

def stop() -> bool:
    """Sends stop command."""
    raise Unimplemented
    msg = b''
    return parse_motor_ack(robot.send_recv(msg, is_motor_ack))

def get_ultrasonics() -> dict:
    """Returns ultrasonic readings."""
    ## TODO: Select appropriate implementation
    ## 1) Polling ultrasonics
    return parse_ultrasonics(robot.send_recv(b'U', is_ultrasonic))
    ## 2) Async only ultrasonics
    return parse_ultrasonics(robot.blocking_recv(is_ultrasonic))

def get_gyroscope() -> dict:
    """Returns gyroscope readings."""
    ## TODO: Select appropriate implementations
    ## 1) Polling gyroscope
    return parse_gyroscope(robot.send_recv(b'G', is_gyroscope))
    ## 2) Async only gyroscope
    return parse_gyroscope(robot.blocking_recv(is_gyroscope))


#################
### MAIN LOOP ###
#################

if __name__ == "__main__":
    robot.store_message = async_messages

    ## TODO: Implement this if using async stuff...
    # Thread(target = robot.receive, daemon=True)

    while True:
        requestor, request = server.recv_multipart()
        match (request[0]):
            case 'F':
                ## Forward
                move(float(request[1:]))
                break

            case _ : ## Fallback
                pass

        msg_resp = b''
        server.send_multipart([requestor, msg_resp])

