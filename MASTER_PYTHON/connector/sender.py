"""Class for controlling robot.

PARAMS:
|- READ_RETRIES
|   How many times to retry reading a motion command response.
|- WRITE_TIMEOUT
|   Timeout on serial.Serial(...).write(...) method.

VARIABLES:
|- CommErrors
|   Raised by almost all Team_11_Robot methods.

CLASSES:
|- Team_11_Robot
|   Serial pseudo-wrapper for communicating with robot.
"""

######################
### BASE LIBRARIES ###
######################
import serial as _serial



########################
### CUSTOM LIBRARIES ###
########################
import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__))) ## Expose local modules

import connector._config  as _config
import connector._encode  as _encode
from connector._request import wait_for_acknowledge, wait_for_reply, wait_for_replies, NoAcknowledge, NoReply
from connector._decode  import decode_progress, decode_ultrasonics

# _ = sys.path.pop() ## Cleanup local modules



##############
### CONFIG ###
##############
READ_RETRIES  = 5
WRITE_RETRIES = 2
WRITE_TIMEOUT = 3 # seconds

CommErrors = (NoAcknowledge, NoReply)



#########################
### PRIVATE FUNCTIONS ###
#########################
def _ultrasonic_lookup(readings: dict) -> dict:
    """Translate "Arduino" names to colloquial names."""
    return readings # dict([_config.ULTR_LOOKUP.get(sensor_id, sensor_id), val] for sensor_id, val in readings.items())



def _cm_to_inch(val: float) -> float:
    return 0.393701 * val



# def _write_retry(write_method):
#     def _retry(*args, **kwargs):
#         for i in range( WRITE_RETRIES ):
#             try:
#                 return write_method(*args, **kwargs)
#             except CommErrors as exc:
#                 if i == WRITE_RETRIES - 1:
#                     raise exc
#                 continue
#     return _retry



############
### MAIN ###
############
class Team_11_Robot:
    """Class for connecing to robot via. Serial or via. Bluetooth.

    PARAMS:
    |- com_port <str>:
    |        Port to connect to robot via. Eg. com_port = "COM12".
    |- serial_timeout <float>:
    |        Seconds timeout for reading serial values.

    METHODS:
    |- write ( msg <bytes> ) -> None:
    |        Writes bytes over serial to robot
    |- readline ( void ) -> bytes:
    |        Reads '\n' terminated string from robot serial
    |- move_forward ( distance <float> ) -> None:
    |        Move forward by {distance} inches
    |- rotate ( angle <float> ) -> None:
    |        Rotate clockwise by {angle} degrees
    |- stop ( void ):
    |        Stop last motion command
    |- is_active( void ) -> bool
    |        Returns True if motor has stopped last motion, else False
    |- progress ( void ) -> float:
    |        Returns percentage; [0.0, 100.0]; along last motion command
    |- led ( r <byte>, g <byte>, b <byte> ) -> None:
    |        Set LED color. Each value in [0, 255]
    |- led_off ( void ) -> None:
    |        Turn LED off
    |- ultrasonics ( void ) -> dict:
    |        Returns dictionary of readings for each ULTRASONIC sensor
    |- ultrasonic_json( number_of_attempts <int> ) -> dict { sensor: readings_list }:
    |        Returns dictionary of lists of {number_of_attempts} readings
    """
    def __init__(self, com_port: str, serial_timeout: float):
        print(f"[Team_11_Robot] Attempting to connect to {com_port}")
        self._com = _serial.Serial(com_port, timeout=serial_timeout, write_timeout=WRITE_TIMEOUT)
        print(f"[Team_11_Robot] Successfully connected on {com_port}!", end="\n\n")



    def write(self, msg: bytes) -> None:
        self._com.write(msg)



    def readline(self) -> bytes:
        msg = self._com.readline()
        return msg



    # @_write_retry
    def move_forward(self, distance: float ) -> None:
        """Move forward by {distance} inches."""
        if distance > 0:
            self.write(_encode.encode_forward(distance))
            wait_for_acknowledge(self, _config.Acknowledges.W_ACK, READ_RETRIES)
        else:
            self.write(_encode.encode_backwards(abs(distance)))
            wait_for_acknowledge(self, _config.Acknowledges.S_ACK, READ_RETRIES)



    # @_write_retry
    def rotate(self, angle: float = None) -> None:
        """Rotate clockwise by {angle} degrees."""
        if angle > 0:
            self.write(_encode.encode_clockwise(angle))
            wait_for_acknowledge(self, _config.Acknowledges.E_ACK, READ_RETRIES)
        else:
            self.write(_encode.encode_counter_clockwise(abs(angle)))
            wait_for_acknowledge(self, _config.Acknowledges.Q_ACK, READ_RETRIES)



    # @_write_retry
    def stop(self) -> None:
        """Stop motors."""
        self.write(_encode.encode_stop())
        wait_for_acknowledge(self, _config.Acknowledges.STOP_ACK, READ_RETRIES)



    # @_write_retry
    def is_active(self) -> bool:
        """Check if motor is in active motion."""
        self.write(_encode.encode_active())
        reply = wait_for_replies(self, [_config.Acknowledges.ACTIVE, _config.Acknowledges.NACTIVE], READ_RETRIES).replace(b'\n', b'').replace(b'\r', b'')
        if reply == _config.Acknowledges.ACTIVE:
            return True
        else:
            return False



    # @_write_retry
    def progress(self) -> float:
        """Return percentage progress along last move."""
        self.write(_encode.encode_progress())
        reply = wait_for_reply(self, _config.PROG_PREFIX, READ_RETRIES)
        return decode_progress(reply)



    # @_write_retry
    def led(self, r: int, g: int, b: int) -> None:
        """Set LED to R={r}; G={g}; B={b} colors."""
        self.write(_encode.encode_led(r, g, b))
        wait_for_acknowledge(self, _config.Acknowledges.LED_ACK, READ_RETRIES)



    # @_write_retry
    def led_off(self) -> None:
        """Turn LED off."""
        self.write(_encode.encode_led(0, 0, 0))
        wait_for_acknowledge(self, _config.Acknowledges.LED_ACK, READ_RETRIES)



    # @_write_retry
    def ultrasonics(self) -> dict[str, float]:
        """Request a dictionary of ULTRASONIC sensor readings."""
        self.write(_encode.encode_ultrasonic())
        return {key: _cm_to_inch(val) for key, val in _ultrasonic_lookup(decode_ultrasonics(wait_for_reply(self, _config.ULTR_PREFIX, READ_RETRIES))).items()}



    # @_write_retry
    def ultrasonic_json(self, number_of_attempts: int) -> dict[str, list[float]]:
        """Request a dictionary of lists of length {number_of_attempts} ULTRASONIC readings."""
        readings = {}
        for _ in range(number_of_attempts):
            self.write(_encode.encode_ultrasonic())
            new_vals: dict = {key: _cm_to_inch(val) for key, val in decode_ultrasonics(wait_for_reply(self, _config.ULTR_PREFIX, READ_RETRIES)).items()}
            for sensor_id, sensor_val in new_vals.items():
                if sensor_id not in readings:
                    readings[sensor_id] = []
                readings[sensor_id].append(sensor_val)
        return _ultrasonic_lookup(readings)
