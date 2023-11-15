####################
### MORE GENERAL ###
####################
## == Expose directory ==
import sys, os; sys.path.append(os.path.dirname(__file__))

## == Import modules ==
import serial_base
import serial_class
import zmq_setup

## == Cleanup ==
sys.path.pop()

######################
### ROBOT-SPECIFIC ###
######################
def import_robot_client():
    try:
        from robot import client
    except ImportError:
        pass
