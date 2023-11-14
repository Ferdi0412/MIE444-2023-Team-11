"""Functions intended to run communicate with the robot."""
from threading import Lock, Thread
from typing    import Callable, Self

## Keep serial to avoid confusing serial.Serial and custom Serial class...
import serial
import zmq

class Unimplemented(Exception):
    """Indicates that something needs implementation."""
    #pass

class MaxRetries(Exception):
    """Intended for when response was not returned within required number of retries."""
    #pass

class ExistingThread(Exception):
    """Intended for when a Thread is already running for Serial class."""
    #pass

class Serial:
    """Class for allowing asynchronous Serial control."""
    MaxRetries = MaxRetries

    def __init__(self, serial_cmd: serial.Serial, serial_resp: serial.Serial, *, mutex_lock: Lock = None, MAX_RETRIES = 20):
        """...
        PARAMS:
        |- serial_cmd <serial.Serial>:
        |       Serial instance to send commands to the robot.
        |- serial_resp <serial.Serial>:
        |       Serial instance to receive messages from the robot.
        |- [mutex_lock] <threading.Lock>:
        |       Used as lock for all receiving methods.
        """
        self.mutex = mutex_lock or Lock()
        self.robot_cmd, self.robot_resp = serial_cmd, serial_resp
        self.MAX_RETRIES = MAX_RETRIES
        self.thread = None

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
    def transmit_raw(self, msg: bytes):
        """Send msg to robot. Assumes encoded message."""
        for byte_ in msg:
            self.robot_cmd.write(byte_)

    def receive(self):
        """Receive a response from the robot. Assumes line-ending (ie. ends in '\n'). Intended for async thread."""
        ## Acquire mutex. If mutex already owned, this will wait until it becomes available again before continuing.
        self.mutex.acquire()
        response = self.robot_resp.readline()
        self.mutex.release()
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
        ## Get mutex to prevent async thread from reading values this might need....
        self.mutex.acquire()

        ## In case of an error anywhere, release mutex, then propogate error...
        try:
            ## Iterate for MAX_RETRIES
            for _ in range(self.MAX_RETRIES):
                ## Assumes all incoming messages end with endline
                msg = self.robot_resp.readline()

                ## Check if desired message, if so, release mutex and return
                if resp_check(msg):
                    self.mutex.release()
                    return msg

                self.store_message(msg)

            ## If iteration ended (MAX_RETRIES reached), raise MaxRetries
            raise self.MaxRetries

        ## Releasing mutex before propogating error...
        except Exception as exc:
            self.mutex.release()
            raise exc

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
        ## Get mutex, to prevent async thread from reading values this call might need.
        ## This will block until mutex is available...
        self.mutex.acquire()

        ## In case of error in transmit_raw, release mutex, then propogate error
        try:
            self.transmit_raw(cmd_msg)

        except Exception as exc:
            self.mutex.release()
            raise exc

        ## Iterate for max MAX_RETRIES
        for _ in range(self.MAX_RETRIES):
            ## Assume all incoming messages end with an endline ('\n', maybe also a '\r' - check C++ Serial.prinln() impl.)
            msg = self.robot_resp.readline()

            ## If resp_check is True, release mutex and return this value
            if resp_check(msg):
                self.mutex.release()
                return msg

            ## If resp_check is False, run store_outcoming and iterate
            self.store_message(msg)

        ## Raise MaxRetries if no appropriate response was received
        raise MaxRetries

    ## TODO: Remove async_ to avoid confusing with something that is actually implementing async...
    def async_recv(self):
        while True:
            ## Use try-catch zmq.Again to keep trying despite timeout
            try:
                msg = self.receive()
            except zmq.Again:
                continue

            try:
                self.store_message(msg)

            except Exception as exc:
                print(f"[Error] -> <{self.__class__.__name__}>.async_recv()")
                print( "...   | -> Thread ending now!")
                raise exc

    def start_async_recv_thread(self):
        """Start async recv thread."""
        if self.thread is not None:
            raise ExistingThread
        self.thread = Thread(target = self.async_recv, daemon=True)
