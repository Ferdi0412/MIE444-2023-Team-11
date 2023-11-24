"""Create a ZMQ server."""

if __name__ != '__main__':
    raise Exception("Only run this as MAIN!")

######################
### BASE LIBRARIES ###
######################
import zmq as _zmq
# import enum   as _enum

########################
### CUSTOM LIBRARIES ###
########################
## Expose robot class
import sys, os; sys.path.append(os.path.dirname(__file__))

from robot_server import NoMotorAck, SingleMotorAck, NoUltrasonics, Team_11_Robot

from robot_server._server import Team_11_Server

_ = sys.path.pop()


IGNORE_ERRORS = False

####################
### SERVER SETUP ###
####################
server = Team_11_Server()

while True:
    try:
        server.start("COM13")

    except Exception as exc:
        if IGNORE_ERRORS:
            continue

        else:
            raise exc
