"""Functions intended to run communicate with the robot."""
# from threading import Lock, Thread, Event
from typing    import Callable, Self

## Keep serial to avoid confusing serial.Serial and custom Serial class...
import serial

class Unimplemented(Exception):
    """Indicates that something needs implementation."""

class MaxRetries(Exception):
    """Intended for when response was not returned within required number of retries."""

class ExistingThread(Exception):
    """Intended for when a Thread is already running for Serial class."""

class BytesNotSent(Exception):
    """Raised when not all bytes of a message are sent."""

class NewSerial:
    """Class for allowing asynchronous Serial control."""
    MaxRetries = MaxRetries

    def __init__(self, serial_cmd: serial.Serial, serial_resp: serial.Serial, *, MAX_RETRIES = 20):
        """...
        PARAMS:
        |- serial_cmd <serial.Serial>:
        |       Serial instance to send commands to the robot.
        |- serial_resp <serial.Serial>:
        |       Serial instance to receive messages from the robot.
        |- [mutex_lock] <threading.Lock>:
        |       Used as lock for all receiving methods.
        """
        self.robot_cmd, self.robot_resp = serial_cmd, serial_resp
        self.MAX_RETRIES = MAX_RETRIES
        self.thread = None
        ## Consider moving kill_quietly to another flag...
        ## If kill_quietly = False, raises InterruptedError on self.recv_thread_kill(...)
        self.kill_quietly = True

    def store_message(self, message: bytes) -> None:
        """Handles outcoming messages which are not inteded for the transmit call which the robot is expected to repond to.

        Please override this.......
        """
        raise Unimplemented

    def set_store_message(self, method: Callable[[Self, bytes], None]) -> None:
        """Override store_message with a new method, which takes a reference to the class instance as the first param.

        Example:
        ## Instantiate class
        robot_comms = Robot(...)

        ## Assign function that DOES NOT take reference to instance
        def opt_1(msg: bytes) -> None:
            print(msg)

        robot_comms.store_message = opt_1
        robot_comms.store_message('Hi there!') # Prints 'Hi there!'

        ## Assign function that takes reference to instance
        def opt_2(self: Robot, msg: bytes) -> None:
            print(f"{self.__class__.__name__} -> {msg}")

        robot_comms.set_store_message(opt_2)
        robot_comms.store_message('Hi there!') # Prints 'Robot -> Hi there!'
        """
        self.store_message = lambda msg: method(self, msg)

    #########################
    ### COMMUNICATE BASIC ###
    #########################
    def send(self, msg: bytes):
        """Send msg to robot. Assumes encoded message."""
        bytes_sent = self.robot_cmd.write(msg)
        if not bytes_sent == len(msg):
            raise BytesNotSent(f"Only {bytes_sent} of {len(msg)} were sent!\nMessage: {msg}")

    def receive(self):
        """Receive a response from the robot. Assumes line-ending (ie. ends in '\n'). Intended for async thread."""
        msg = self.robot_resp.readline()
        self.store_message(msg)
        return response


    def blocking_recv(self, resp_check: Callable[[bytes], bool]) -> bytes:
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
        ## Iterate for MAX_RETRIES
        for _ in range(self.MAX_RETRIES):
            ## Assumes all incoming messages end with endline
            msg = self.robot_resp.readline()

            self.store_message(msg)

            if resp_check(msg):
                return msg

        ## If iteration ended (MAX_RETRIES reached), raise MaxRetries
        raise self.MaxRetries

    def send_recv(self, cmd_msg: bytes, resp_check: Callable[[bytes], bool]) -> bytes:
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
        self.send(cmd_msg)

        ## Iterate for max MAX_RETRIES
        for _ in range(self.MAX_RETRIES):
            ## Assume all incoming messages end with an endline ('\n', maybe also a '\r' - check C++ Serial.prinln() impl.)
            msg = self.robot_resp.readline()

            if resp_check(msg):
                return msg

            ## If resp_check is False, run store_outcoming and iterate
            self.store_message(msg)
        ## Raise MaxRetries if no appropriate response was received
        raise MaxRetries
