"""Class for controlling robot."""

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
from connector._request import NoAcknowledge, NoReply, wait_for_acknowledge, wait_for_reply, wait_for_replies
from connector._decode  import decode_progress, decode_ultrasonics

_ = sys.path.pop() ## Cleanup local modules



#########################
### PRIVATE FUNCTIONS ###
#########################
def _ultrasonic_lookup(readings: dict) -> dict:
    """Translate "Arduino" names to colloquial names."""
    return dict([_config.ULTR_LOOKUP.get(sensor_id, sensor_id), val] for sensor_id, val in readings.items())



############
### MAIN ###
############
class Team_11_Robot:
    def __init__(self, com_port: str, serial_timeout: float):
        self._com = _serial.Serial(com_port, timeout=serial_timeout)
        print(f"Connected on {com_port}!")



    def write(self, msg) -> None:
        self._com.write(msg)



    def move_forward(self, distance: float = None) -> None:
        """Move forward by {distance} inches."""
        if distance > 0:
            self.write(_encode.encode_forward(distance))
            wait_for_acknowledge(self._com, _config.Acknowledges.W_ACK)
        else:
            self.write(_encode.encode_backwards(distance))
            wait_for_acknowledge(self._com, _config.Acknowledges.S_ACK)



    def rotate(self, angle: float = None) -> None:
        """Rotate clockwise by {angle} degrees."""
        if angle > 0:
            self.write(_encode.encode_clockwise(angle))
            wait_for_acknowledge(self._com, _config.Acknowledges.E_ACK)
        else:
            self.write(_encode.encode_counter_clockwise(angle))
            wait_for_acknowledge(self._com, _config.Acknowledges.Q_ACK)



    def stop(self) -> None:
        """Stop motors."""
        self.write(_encode.encode_stop())
        wait_for_acknowledge(self._com, _config.Acknowledges.STOP_ACK)



    def is_active(self) -> bool:
        """Check if motor is in active motion."""
        self.write(_encode.encode_active())
        reply = wait_for_replies(self._com, [_config.Acknowledges.ACTIVE, _config.Acknowledges.NACTIVE])
        if reply == _config.Acknowledges.ACTIVE:
            return True
        else:
            return False



    def progress(self) -> float:
        """Return percentage progress along last move."""
        self.write(_encode.encode_progress())
        reply = wait_for_reply(self._com, _config.PROG_PREFIX)
        return decode_progress(reply)



    def led(self, r: int, g: int, b: int) -> None:
        self.write(_encode.encode_led(r, g, b))
        wait_for_acknowledge(self._com, _config.Acknowledges.LED_ACK)



    def led_off(self) -> None:
        self.write(_encode.encode_led(0, 0, 0))
        wait_for_acknowledge(self._com, _config.Acknowledges.LED_ACK)



    def ultrasonics(self) -> dict[str, float]:
        self.write(_encode.encode_ultrasonic())
        return _ultrasonic_lookup(decode_ultrasonics(wait_for_reply(self._com, _config.ULTR_PREFIX)))



    def ultrasonic_json(self, number_of_attempts: int) -> dict[str, list[float]]:
        readings = {}
        for _ in range(number_of_attempts):
            self.write(_encode.encode_ultrasonic())
            new_vals: dict = decode_ultrasonics(wait_for_reply(self._com, _config.ULTR_PREFIX))
            for sensor_id, sensor_val in new_vals.items():
                if sensor_id not in readings:
                    readings[sensor_id] = []
                readings[sensor_id].append(sensor_val)
        return _ultrasonic_lookup(readings)