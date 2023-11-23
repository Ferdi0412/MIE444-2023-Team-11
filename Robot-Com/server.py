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
import sys, os; sys.path.append(os.path.dirname(__file__)) ## Expose local modules

from control_robot import NoMotorAck, SingleMotorAck, NoUltrasonics, Team_11_Robot

_ = sys.path.pop() ## Cleanup local modules

