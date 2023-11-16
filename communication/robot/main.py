"""Script to start server.

"""
import sys, os; sys.path.append(os.path.dirname(__file__))

from robot_class    import Robot
from ..zmq_setup     import get_publisher, get_server
from ..serial_base   import setup_serial

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

if __name__ == '__main__':
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
