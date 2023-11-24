from typing import Any
from json   import loads as _json_loads

# led_t = NewType('Colour', int | bytes | str)

########################
### CUSTOM LIBRARIES ###
########################
## Expose local modules
import sys, os; sys.path.append(os.path.dirname(__file__))

## Import local modules
from control_robot import Team_11_Robot, NoMotorAck, SingleMotorAck, NoUltrasonics

## Cleanup
_ = sys.path.pop()


#####################
### ERROR CLASSES ###
#####################
_MOTOR_EXCEPTION      = (NoMotorAck, SingleMotorAck,)
_ULTRASONIC_EXCEPTION = NoUltrasonics

class FAILED (Exception):
    """Server failed to handle request... You did nothing wrong (I think)."""

def try_until_failure(some_method):
    def keep_trying(*args, **kwargs):
        while True:
            try:
                return some_method(*args, **kwargs)
            except Exception:
                continue
    return keep_trying

##############
### CLIENT ###
##############
class Team_11_Client:
    def __init__(self, com_port: str):
        self._client = Team_11_Robot(com_port)

    @staticmethod
    def _hex(val: str | bytes) -> int:
        """Translate hex input to an integer."""
        if isinstance(val, str | bytes):
            return ord(val)
        return val



    @try_until_failure
    def move_forward(self, distance: float) -> float:
        """Send move forward command, returns movement from last movement commad."""
        try:
            self._client.move_forward(distance)
        except _MOTOR_EXCEPTION:
            return FAILED



    @try_until_failure
    def rotate(self, angle: float) -> None:
        """Send rotate command."""
        try:
            self._client.rotate(angle)
            return
        except _MOTOR_EXCEPTION:
            raise FAILED



    @try_until_failure
    def stop(self) -> float:
        """Stop robot."""
        try:
            self._client.stop()
        except _MOTOR_EXCEPTION:
            raise FAILED



    @try_until_failure
    def is_active(self) -> bool:
        """Check if robot is moving."""
        try:
            return self._client.get_active()
        except _MOTOR_EXCEPTION:
            raise FAILED



    @try_until_failure
    def progress(self) -> float:
        """Returns progress, in inches, along last move."""
        try:
            return self._client.get_progress()
        except _MOTOR_EXCEPTION:
            return FAILED



    @try_until_failure
    def led(self, r: int | bytes | str, g: int | bytes | str, b: int | bytes | str) -> None:
        """Set LED on robot. Value inputs in range [0, 255]."""
        ## Typecase r, g, b to <int>
        r = self._hex(r)
        g = self._hex(g)
        b = self._hex(b)

        ## Send LED command
        self._client.set_led(r, g, b)



    @try_until_failure
    def led_off(self) -> None:
        """Set LED to OFF."""
        self._client.set_led_off()



    @try_until_failure
    def ultrasonic(self) -> list[float]:
        """Get inch readings for values."""
        try:
            return self._client.get_ultrasonics()
        except _ULTRASONIC_EXCEPTION:
            raise FAILED



    @try_until_failure
    def ultrasonic_json(self, measurment_count: int) -> dict[str, list[float]]:
        """Return json with lists of inch readings from ultrasonic sensors."""
        try:
            return self._client.get_ultrasonics_DataFrame(measurment_count)
        except _ULTRASONIC_EXCEPTION:
            return FAILED

