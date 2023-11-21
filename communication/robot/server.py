"""Implement translation from server/request API to robot API using robot_class."""
from zmq    import Again
from typing import Dict
from json   import loads, dumps

import sys, os

##################
###   CUSTOM   ###
### LIBRARIES  ###
##################
## 1) General
## == Expose them ==
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

## == Import them ==
from communication.zmq_setup   import get_publisher, get_server
from communication.serial_base import setup_serial

## == Cleanup ==
sys.path.pop()

## 2) Our robot-specific
## == Expose them ==
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

## == Import them ==
from robot.robot_class import Robot
## == Cleanup ==
sys.path.pop()



#################
###   WRAPPER ###
###    CLASS  ###
#################
OWNERSHIP_REQUIRED = b'OWNERSHIP-REQUIRED'
ALREADY_OWNED      = b'ALREADY-OWNED'
INVALID_REQUEST    = b'INVALID-REQUEST'



#################
###   WRAPPER ###
###    CLASS  ###
#################
class RobotServer:
    def __init__(self, com_out: str, com_in: str):
        self.server     = get_server()
        self.publisher  = get_publisher()
        self.com_out    = setup_serial(com_out)
        self.owner      = None
        if com_out == com_in:
            self.com_in = self.com_out
        else:
            self.com_in = setup_serial(com_in)
        self.robot      = Robot(self.com_out, self.com_in)

    def is_owner(self, requestor: bytes) -> bool:
        return self.owner == requestor

    def _map_request(self, requestor: bytes, request: bytes) -> bytes:
        """Handles request, and returns response for user..."""
        req_type, *req_body = request.split(b'\n')
        # req_body = b'\n'.join(req_body or [])

        ## == ROBOT STUFF ==
        match ( req_type ):
            case b'MOVE':
                if self.is_owner(requestor):
                    fwd, right = req_body
                    fwd        = float(fwd.decode('utf-8'))
                    right      = float(right.decode('utf-8'))
                    return dumps(self.robot.move(fwd, right)).encode('utf-8')

                else:
                    return OWNERSHIP_REQUIRED

            case b'ROTATE':
                if self.is_owner(requestor):
                    angle, = req_body
                    angle  = float(angle.decode('utf-8'))
                    return dumps(self.robot.rotate(angle)).encode('utf-8')

                else:
                    return OWNERSHIP_REQUIRED

            case b'STOP':
                if self.is_owner(requestor):
                    return dumps(self.robot.stop()).encode('utf-8')

                else:
                    return OWNERSHIP_REQUIRED

            case b'LED':
                if self.is_owner(requestor):
                    turn_on = True if req_body else False
                    self.robot.led(turn_on)
                    return b''

                else:
                    return OWNERSHIP_REQUIRED

            case b'IN-MOTION':
                return dumps(self.robot.active()).encode('utf-8')

            case b'PROGRESS':
                return dumps(self.robot.progress()).encode('utf-8')

            case b'ULTRASONIC':
                return dumps(self.robot.get_ultrasonic_readings()).encode('utf-8')

            ## == SERVER ONLY STUFF ==
            case b'CLAIM-OWN':
                if self.owner is None or req_body:
                    self.owner = requestor
                    return b''
                else:
                    return OWNERSHIP_REQUIRED

            case b'IS-OWNER':
                return str(self.is_owner(requestor)).encode('utf-8')

            case b'HAS-OWNER':
                return str(self.owner is not None).encode('utf-8')

            case b'REV-OWN':
                if self.owner is not None and not self.is_owner(requestor):
                    return OWNERSHIP_REQUIRED
                self.owner = None
                return b''


            ## TODO: Implement something of form of following:
            case b'SET-POS':
                pass ## Set "localized" position from automation

            case b'IS-LOC':
                pass ## Check if has been "localized"

            case b'IS-PARALLEL':
                pass ## Check if robot is parallel

            case _:
                return INVALID_REQUEST
        pass ## Map incoming requests to robot msgs here...

    def main(self):
        """Similar to loop() in Arduino code. This is the main looping function..."""
        try:
            requestor, request = server.recv_multipart()
            return self._map_request(requestor, request)

        ## No requests...
        except Again:
            self.robot.receive()



################
###   MAIN   ###
################
if __name__ == '__main__':
    print("Main started!\n")

    server    = get_server()
    publisher = get_publisher()
