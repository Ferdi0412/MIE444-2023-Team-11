"""Developed to run on Windows, and assumes connection is via. bluetooth.

This is because Windows creates a virtual COM connection for bluetooth, and
the robot (which uses an ESP32 with integrated bluetooth), will have 2 established
COMs.
1. Outgoing for messages from computer to robot.
2. Incoming for messages originating from robot, to computer.

Intentions:
1. Support pure command message (ie. stop)
|  -> These should always succeed so long as the connection is there.
2. Support poll-response type activity (ie. move)
|  -> These should have some form of response/acknowledgement
3. Support pure outcoming messages (eg. ultrasonics constantly being sent)
|  -> These should be more auxilliary or less time-sensitive/action-dependent
"""
from threading import Thread, Lock
from typing import Callable

import sys, os
sys.path.append(os.path.dirname(__file__))

from zmq_setup import get_publisher, get_server
from serial_comm import setup_serial, decode_float, decode_int16, decode_int32

class Unimplemented (Exception):
    pass

class MaxRetries (Exception):
    """Intended for when response was not returned within required number of retries."""

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

mutex = Lock()

## Non-blocking response connection, in order to use for publisher and individual command responses...
robot_cmd  = setup_serial(COM_OUT, ROB_TIMEOUT)
robot_resp = setup_serial(COM_IN,  ROB_TIMEOUT)

#########################
### COMMUNICATE BASIC ###
#########################
def receive():
    """Receive a response from the robot. Assumes line-ending (ie. ends in '\n'). Intended for async thread."""
    ## Acquire mutex. If mutex already owned, this will wait until it becomes available again before continuing.
    mutex.acquire()
    response = robot_resp.readline()
    mutex.release()
    return response

def blocking_recv(resp_check: Callable[[bytes], bool]) -> bytes:
    """Returns first message that returns True when run inside Callable.
    Raises MaxRetries.

    Intended for example for a Ultrasonic reading, if these are released on regular intervals without
    having a "poll" implementation for these on the robot.

    PARAMS:
    |- resp_check <Callable(bytes) -> bool>:
    |    Function that receives incoming message and returns True or False.
    |    If True, corresponding message is returned.
    |    If no value returns True within MAX_RETRIES, MaxRetries is raised.
    """
    ## Get mutex to prevent async thread from reading values this might need....
    mutex.acquire()

    ## In case of an error anywhere, release mutex, then propogate error...
    try:
        ## Iterate for MAX_RETRIES
        for _ in range(MAX_RETRIES):
            ## Assumes all incoming messages end with endline
            msg = robot_resp.readline()

            ## Check if desired message, if so, release mutex and return
            if resp_check(msg):
                mutex.release()
                return msg

            store_outcoming(msg)

        ## If iteration ended (MAX_RETRIES reached), raise MaxRetries
        raise MaxRetries

    ## Releasing mutex before propogating error...
    except Exception as exc:
        mutex.release()
        raise exc

def send_recv(cmd_msg: bytes, resp_check: Callable[[bytes], bool]) -> bytes:
    """Sends a message to the robot, then waits for a messge that returns True when input into resp_check.
    Raises MaxRetries.

    Intended for example for example for polling Ultrasonics if robot has a "request ultrasonics" implementation.

    PARAMS:
    |- cmd_msg <bytes>:
    |      Message to send to robot.
    |- resp_check <Callable(bytes) -> bool>:
    |      Function that receives incoming message and returns True or False. If True, the corresponding
    |      message is returned.
    |      If no value returns True from resp_check within MAX_RETRIES, MaxRetries is raised.
    """
    ## Get mutex, to prevent async thread from reading values this call might need.
    ## This will block until mutex is available...
    mutex.acquire()

    ## In case of error in transmit_raw, release mutex, then propogate error
    try:
        transmit_raw(cmd_msg)

    except Exception as exc:
        mutex.release()
        raise exc

    ## Iterate for max MAX_RETRIES
    for _ in range(MAX_RETRIES):
        ## Assume all incoming messages end with an endline ('\n', maybe also a '\r' - check C++ Serial.prinln() impl.)
        msg = robot_resp.readline()

        ## If resp_check is True, release mutex and return this value
        if resp_check(msg):
            mutex.release()
            return msg

        ## If resp_check is False, run store_outcoming and iterate
        store_outcoming(msg)

    ## Raise MaxRetries if no appropriate response was received
    raise MaxRetries

def store_outcoming(msg: bytes):
    """Handles outcoming messages which are not inteded for the transmit call which the robot is expected to repond to."""
    raise Unimplemented

def transmit_raw(msg: bytes):
    """Send msg to robot. Assumes encoded message."""
    for byte_ in msg:
        robot_cmd.write(byte_)

#####################
### SEND MESSAGES ###
#####################
def move(fwd: float, right: float) -> bool:
    """Send move command. Returns True if successful movement. Negative values indicate opposite direction."""
    raise Unimplemented
    ## TODO: Check encoding
    msg = b'{fwd}//{right}'
    return parse_motor_ack(send_recv(msg, is_motor_ack))

def rotate(clockwise: float) -> bool:
    """Sends move command. Returns True if successful movement. Negative value is counter-clockwise."""
    raise Unimplemented
    msg = b''
    return parse_motor_ack(send_recv(msg, is_motor_ack))

def stop() -> bool:
    """Sends stop command."""
    raise Unimplemented
    msg = b''
    return parse_motor_ack(send_recv(msg, is_motor_ack))

def get_ultrasonics() -> dict:
    """Returns ultrasonic readings."""
    ## TODO: Select appropriate implementation
    ## 1) Polling ultrasonics
    return parse_ultrasonics(send_recv(b'U', is_ultrasonic))
    ## 2) Async only ultrasonics
    return parse_ultrasonics(blocking_recv(is_ultrasonic))

def get_gyroscope() -> dict:
    """Returns gyroscope readings."""
    ## TODO: Select appropriate implementations
    ## 1) Polling gyroscope
    return parse_gyroscope(send_recv(b'G', is_gyroscope))
    ## 2) Async only gyroscope
    return parse_gyroscope(blocking_recv(is_gyroscope))

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


