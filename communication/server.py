import zmq
from threading import Thread
from typing import Dict

## Expose local files
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

robot.owner_id = None

class OwnershipError (Exception):
    """Raised for requests that require ownership/elevation."""
    pass

class OwnershipConflict (Exception):
    """Raised for CLAIM-OWN witout high_priority, if already owned."""
    pass

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

def check_motion() -> bool:
    """Retrieves whether the robot is in motion or not."""
    raise Unimplemented

def check_progress() -> Dict[str, float]:
    """Retrieves progress along motion of robot."""
    raise Unimplemented

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



##########################
### PERMISSIONS HANDLE ###
##########################
def is_owner(client_id: bytes) -> bool:
    """Returns True if the client_id is the ID of the robot Owner."""
    return ( client_id == robot.owner_id )

def has_owner() -> bool:
    """Returns True if the robot is owned."""
    return ( robot.owner_id is not None )

def require_ownership(client_id: bytes) -> None:
    """Raises OwnershipError."""
    if not is_owner(client_id):
        raise OwnershipError



######################
### REQUEST HANDLE ###
######################
def handle_request(client_id: bytes, msg: bytes) -> bytes | None:
    """Handle incoming request, and return response to send."""
    # req_head, req_data, *_ = request.split(b'\n')
    req_head, *req_data = msg.split(b'\n')
    req_data = b'\n'.join(req_data)

    ## Handle request according to format
    match (req_head):

        ## Actions that require Ownership/Elevation
        case b'MOVE':
            require_ownership(client_id)
            fwd, right = req_data.decode('utf-8').split(';')
            return move(float(fwd), float(right))

        case b'ROTATE':
            require_ownership(client_id)
            angle = float( req_data.decode('utf-8') )
            return rotate(angle)

        case b'STOP':
            require_ownership(client_id)
            return stop()

        ## Requests that do not require ownership/elevation
        case b'IN-MOTION':
            return check_motion()

        case b'PROGRESS':
            return check_progress()

        case b'PROGRESS-ALL':
            return min( check_progress().values() )

        case b'ULTRASONIC':
            return get_ultrasonics()

        case b'GYROSCOPE':
            return get_gyroscope()

        ## Server Ownership/Elevation control
        case b'CLAIM-OWN':
            if not req_data and has_owner():
                raise OwnershipConflict
            robot.owner_id = client_id
            return None

        case b'IS-OWNER':
            return is_owner(client_id)

        case b'HAS-OWNER':
            return has_owner()

        case b'REV-OWN':
            if not is_owner(client_id):
                raise OwnershipConflict
            robot.owner_id = None
            return None

        ## Fallback
        case _:
            raise Unimplemented

#################
### MAIN LOOP ###
#################
if __name__ == "__main__":
    ## Setup publishing of async values...
    robot.store_message = async_messages
    Thread(target = robot.receive, daemon=True)

    ## Setup handling of direct requests...
    while True:
        ## Catch zmq.Again to allow timeouts, in order to kill program with KeyboardExit after .recv(...) times out
        try:
            requestor, request = server.recv_multipart()

        except zmq.Again:
            continue

        try:
            msg_resp = handle_request(requestor, request)

        ## Check if invalid ownership assigment
        except OwnershipConflict:
            msg_resp = b'OWNERSHIP_CONFLICT'

        ## Check if ownership required
        except OwnershipError:
            msg_resp = b'OWNERSHIP_REQUIRED'

        ## Send response
        server.send_multipart([requestor, msg_resp])

