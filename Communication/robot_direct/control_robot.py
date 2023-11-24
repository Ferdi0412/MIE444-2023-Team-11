"""Functions for controlling the robot.

Requires the following modules:
|-> pyserial
"""
## TODO: Add handling in _await_... for when a '\n' character is in the measurement...

######################
### BASE LIBRARIES ###
######################
import serial as _serial
import time   as _time
import pandas as _pandas

########################
### CUSTOM LIBRARIES ###
########################
## Expose local modules
import sys, os; sys.path.append(os.path.dirname(__file__))

## Import local modules
import robot_decode as _robot_decode
import robot_encode as _robot_encode
import robot_config as _config

## Cleanup
_ = sys.path.pop()

#######################
### EXPECTED ERRORS ###
#######################
class SingleMotorAck (Exception):
    """Only a single motor acknowledged/responded a given request."""

class NoMotorAck (Exception):
    """No motor acknowledged/responded to a given request."""

class NoUltrasonics (Exception):
    """No response to an Ultrasonic request."""

####################################
### CLASS FOR WORKING WITH ROBOT ###
####################################
class Team_11_Robot:
    """Class for connecting to our robot and controlling it.

    PARAMS:
    |- outgoing_coms <str>
    |         COM port to find our robot
    |- [read_timeout] <float>
    |         Timeout for serial connections (default 0.0 seconds)
    |- [read_retries] <int>
    |         Number of retries to fetch response from robot (default 10)
    |- [retry_sleep] <float>
    |         Time to sleep between retries when fetching response from robot (default 0.1)
    """
    def __init__(self, outgoing_coms: str, *, read_timeout: float = 0.3, read_retries: int = 10, retry_sleep: float = 0.0) -> bytes:
        print(f"Connecting to the robot on {outgoing_coms}...")
        self._serial: _serial.Serial = _serial.Serial(outgoing_coms, timeout=read_timeout)
        self._read_retries = read_retries
        self._retry_sleep   = retry_sleep
        print("Setup!\n")
        self._x()



    ##############
    ## INTERNAL ##
    ##############
    ## Functions of format:
    ## _await_robot_[...] -> try fetch response of both motor's

    def _await_robot_active(self, message_type: int) -> tuple[bool | None, bool | None]:
        """Try to read response from robot for a command that returns it's active state."""
        left_active, right_active = None, None
        for _ in range(self._read_retries):
            msg = self._serial.readline()

            ## If no message, or invalid message, sleep and then continue
            if not (msg and msg[0] == message_type):
                print(f"[_await_robot_active] Received invalid value...: {msg}")
                _time.sleep(self._retry_sleep)
                continue

            ## Sometimes a char in the middle is '\n', account for this
            try:
                while len(msg) < _config.MSG_LEN_ACTIVE:
                    print("[_await_robot_active(...)] -> '\\n' char received")
                    print("                         | -> trying again...")
                    print(f"                         | -> {msg}")
                    ## msg expected to get longer each iteration,
                    ## as value should at least contain '\n',
                    ## or be None
                    msg += self._await_any()

            ## If self._await_any fails, break such that any found results get returned
            except TypeError:
                break

            motor_id, is_active = _robot_decode.decode_active(msg)

            if motor_id == _config.MOTOR_LEFT:
                left_active = is_active

            elif motor_id == _config.MOTOR_RIGHT:
                right_active = is_active

            if left_active is not None and right_active is not None:
                break

        return left_active, right_active
        ## ~_await_robot_active(...)



    def _await_robot_progress(self, message_type: int) -> tuple[float | None, float | None]:
        """Try to read response from robot for a command that returns it's progress."""
        left_progress, right_progress = None, None

        for _ in range(self._read_retries):
            msg = self._serial.readline()

            ## If no message, or invalid message, sleep and then continue
            if not (msg and msg[0] == message_type):
                print(f"[_await_robot_progress] Received invalid value...: {msg}")
                _time.sleep(self._retry_sleep)
                continue

            ## Sometimes a char in the middle is '\n', account for this
            try:
                while len(msg) < _config.MSG_LEN_PROGRESS:
                    print("[_await_robot_progress(...)] -> '\\n' char received")
                    print("                           | -> trying again...")
                    print(f"                           | -> {msg}")
                    ## msg expected to get longer each iteration,
                    ## as value should at least contain '\n',
                    ## or be None
                    msg += self._await_any()

            ## If self._await_any fails, break such that any found results get returned
            except TypeError:
                break


            motor_id, motor_progress = _robot_decode._decode_progress(msg)

            if motor_id == _config.MOTOR_LEFT:
                # print(msg)
                left_progress = motor_progress

            elif motor_id == _config.MOTOR_RIGHT:
                # print(msg)
                right_progress = motor_progress

            if left_progress is not None and right_progress is not None:
                break

        return left_progress, right_progress
        ## ~_await_robot_progress(...)



    def _await_msg(self, message_type: int) -> bytes | None:
        """Try to read value starting with message_type."""
        for _ in range(self._read_retries):
            msg = self._serial.readline()

            ## If appropriate message received, return it
            if msg and msg[0] == message_type:
                return msg

            ## Else, sleep and then continue
            _time.sleep(self._retry_sleep)

        return
        ## ~_await_msg(...)



    def _await_any(self) -> bytes | None:
        """Return as soon as any value is returned."""
        for _ in range(self._read_retries):
            msg = self._serial.readline()

            if msg:
                return msg

        return
        ## ~_await_any(...)



    @staticmethod
    def _select_progress(left_progress: float, right_progress: float) -> float:
        """Determines how Robot progress is determined from either motor."""
        return min(left_progress, right_progress)



    def _x(self) -> None:
        """Trigger 'X' message on sensor board."""
        self._serial.write(b'X')



    def _get_ultrasonics_Series(self) -> _pandas.Series:
        return _pandas.Series( self.get_ultrasonics(), index=_config.ULTRASONIC_ORDER )



    ## PUBLIC ##
    ############
    def write(self, msg: bytes) -> None:
        """Write message to Serial connection."""
        self._serial.write(msg)



    def read(self) -> bytes:
        """Read message from Serial connection."""
        return self._serial.read()



    def readline(self) -> bytes:
        """Read message from Serial connection."""
        return self._serial.readline()



    def readlines(self) -> list[bytes]:
        """Read message(s) from Serial connection."""
        return self._serial.readlines()



    @staticmethod
    def encode_int(val) -> bytes:
        """"Encode an integer value to bytes."""
        return _robot_encode._encode_int(val)



    @staticmethod
    def encode_float(val) -> bytes:
        """Encode a float value to bytes."""
        return _robot_encode._encode_float(val)



    @staticmethod
    def encode_char(val) -> bytes:
        """Encode a char value to bytes."""
        return _robot_encode._encode_char(val)



    def stop(self) -> float:
        """Sends command to stop robot.
        Returns progress along previous move (in inches).
        Raises NoMotorAck, SingleMotorAck.
        """
        print("STOP ROBOT!")
        ## Encode and send command
        msg = _robot_encode.encode_stop()
        self._serial.write(msg)

        ## Check for response
        left_progress, right_progress = self._await_robot_progress(_robot_decode.Message.STOP)

        ## Raise appropriate errors
        if left_progress is None and right_progress is None:
            raise NoMotorAck

        elif left_progress is None or right_progress is None:
            raise SingleMotorAck

        ## Return robot progress
        return self._select_progress(left_progress, right_progress)



    def move_forward(self, distance: float, speed: float = 40.0) -> float:
        """Send command to move robot forward by {distance} inches.
        Returns progress along previous move (in inches).
        Raises NoMotorAck, SingleMotorAck.
        """
        print(f"Requesting to move {distance} inches")
        ## Encode and send command
        msg = _robot_encode.encode_forward(distance, speed)

        self._serial.write(msg)

        ## Get progress along last move
        left_progress, right_progress = self._await_robot_progress(_robot_decode.Message.MOVE)

        ## If no motor responded, just raise error.
        if left_progress is None and right_progress is None:
            raise NoMotorAck

        ## If a single motor responded, stop motion, then raise error.
        elif left_progress is None or right_progress is None:
            self.stop()
            raise SingleMotorAck

        ## Return robot progress
        return self._select_progress(left_progress, right_progress)



    def rotate(self, angle: float) -> None:
        """Sends command to rotate robot by {angle} degrees.
        Raises NoMotorAck, SingleMotorAck.
        """
        print(f"Requesting a ROTATION of {angle} degrees")
        ## Encode and send message
        msg = _robot_encode.encode_rotate(angle)
        self._serial.write(msg)

        ## Wait for confirmation
        left_ack, right_ack = self._await_robot_progress(_robot_decode.Message.MOVE)

        ## If no motor respondsd, just raise error.
        if left_ack is None and right_ack is None:
            raise NoMotorAck

        ## If single motor responded, stop motion, then raise error.
        elif left_ack is None or right_ack is None:
            self.stop()
            raise SingleMotorAck

        ## Return nothing
        return



    def get_progress(self) -> float:
        """Requests progress (in inches) along latest movement (assumes linear).
        Raises NoMotorAck, SingleMotorAck.
        """
        print("Requesting PROGRESS")
        ## Encode and send message
        msg = _robot_encode.encode_progress()
        self._serial.write(msg)

        ## Wait for response
        left_progress, right_progress = self._await_robot_progress(_robot_decode.Message.PROGRESS)

        ## Raise any appropriate errors...
        if left_progress is None and right_progress is None:
            raise NoMotorAck
        elif left_progress is None or right_progress is None:
            raise SingleMotorAck

        ## Return robot progress
        return self._select_progress(left_progress, right_progress)



    def get_active(self) -> bool:
        """Requests if robot is moving.
        Raises NoMotorAck, SignleMotorAck.
        """
        print("Requesting ACTIVE status")
        ## Encode and send message
        msg = _robot_encode.encode_active()
        self._serial.write(msg)

        ## Wait for response
        left_active, right_active = self._await_robot_active(_robot_decode.Message.ACTIVE)

        ## Raise appropriate errors...
        if left_active is None and right_active is None:
            raise NoMotorAck
        elif left_active is None or right_active is None:
            raise SingleMotorAck

        ## Returns True if either motor is active
        return left_active or right_active



    def set_led(self, red: int, green: int, blue: int) -> None:
        """Sets LED to a given colour, by RGB values."""
        ## Encode and send message, no response so nothing to check
        msg = _robot_encode.encode_led(red, green, blue)
        self._serial.write(msg)
        print(f"Setting LED state to R{red} G{green} B{blue}\n{msg}")
        return



    def set_led_off(self) -> None:
        """Turns LED off."""
        print("Turning LED off...")
        ## Encode and send message, nothing to check
        msg = _robot_encode.encode_led(0, 0, 0)
        self._serial.write(msg)
        return



    def get_ultrasonics(self) -> list[float]:
        """Returns list of LED readings.
        Raises NoUltrasonics.
        """
        print("Requesting ultrasonics...")
        ## Encode and send message
        msg = _robot_encode.encode_ultrasonics()
        self._serial.write(msg)

        ## Wait for response
        msg = self._await_msg(_robot_decode.Message.ULTRASONIC)

        ## Sometimes a char in the middle is '\n', account for this
        try:
            while len(msg) < _config.MSG_LEN_ULTRASONIC:
                print("[get_ultrasonics(...)] -> '\\n' char received")
                print("                     | -> trying again...")
                print(f"                     | -> {msg}")
                print(_config.MSG_LEN_ULTRASONIC)
                ## msg expected to get longer each iteration,
                ## as value should at least contain '\n',
                ## or be None
                msg += self._await_any()

        ## If self._await_any fails, break such that any found results get returned
        except TypeError:
            raise NoUltrasonics

        ## Try to decode message
        if msg is not None:
            return _robot_decode.decode_ultrasonic(msg)

        ## Otherwise raise appropriate error
        raise NoUltrasonics




    def get_ultrasonics_DataFrame(self, count: int) -> _pandas.DataFrame:
        """Return a pandas DataFrame containing several readings of the ultrasonic values."""
        df = self._get_ultrasonics_Series().to_frame()
        for i in range(1, count):
            _columns = [*df.columns, i]
            df = _pandas.concat([df, self._get_ultrasonics_Series()], axis=1)
            df.columns = _columns
        return df.T
