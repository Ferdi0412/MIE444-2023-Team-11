"""Derived from function copied from simmer-python-main/scripts/dead_reckoning.py

"""

import socket, struct, math

### Network Setup ###
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT_TX = 61200     # The port used by the *CLIENT* to receive
PORT_RX = 61201     # The port used by the *CLIENT* to send data

def _bytes_to_list(msg):
    num_responses = int(len(msg)/8)
    data = struct.unpack("%sd" % str(num_responses), msg)
    return data

def _transmit(data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT_TX))
        s.send(data.encode('utf-8'))
    return _receive()

def _receive():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            s2.connect((HOST, PORT_RX))
            responses_raw = s2.recv(1024)
            if responses_raw:
                res = _bytes_to_list(responses_raw)[0]
                return res

ULTRASONICS = {"F": '0', 'FR': "5", "BR": "4", "B": "1", "FL": "2", "BL": "3"}

## Wrapper Class ##
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
    def __init__(self, *args, **kwargs):
        pass

    def move_forward(self, distance: float ) -> None:
        """Move forward by {distance} inches."""
        _transmit('xx')
        _transmit(f'w0-{distance}')



    def rotate(self, angle: float = None) -> None:
        """Rotate clockwise by {angle} degrees."""
        _transmit('xx')
        _transmit(f'r0-{angle}')



    def stop(self) -> None:
        """Stop motors."""
        _transmit('xx')



    def is_active(self) -> bool:
        """Check if motor is in active motion."""
        return _transmit('w0-0') != math.inf



    def progress(self) -> float:
        """Return percentage progress along last move."""
        pass



    def led(self, r: int, g: int, b: int) -> None:
        """Set LED to R={r}; G={g}; B={b} colors."""
        pass



    def led_off(self) -> None:
        """Turn LED off."""
        pass



    def ultrasonics(self) -> dict[str, float]:
        """Request a dictionary of ULTRASONIC sensor readings."""
        return { u_name: _transmit(f"u{u_id}") for u_name, u_id in ULTRASONICS.items() }



    def ultrasonic_json(self, number_of_attempts: int) -> dict[str, list[float]]:
        """Request a dictionary of lists of length {number_of_attempts} ULTRASONIC readings."""
        values = {}
        for _ in range(number_of_attempts):
            for key, val in self.ultrasonics().items():
                if key not in values:
                    values[key] = []
                values[key] = val
        return values
