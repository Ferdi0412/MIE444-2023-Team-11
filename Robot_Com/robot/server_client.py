from typing import Any
from json   import loads as _json_loads

# led_t = NewType('Colour', int | bytes | str)

########################
### CUSTOM LIBRARIES ###
########################
## Expose local modules
import sys, os; sys.path.append(os.path.dirname(__file__))

## Import local modules
from _socket_wrapper import get_client as _get_client, SocketTimeout, _zmq
import config as _config

## Cleanup
_ = sys.path.pop()


#####################
### ERROR CLASSES ###
#####################
class FAILED (Exception):
    """Server failed to handle request... You did nothing wrong (I think)."""

class NO_CONNECTION (Exception):
    """Server is not connected to robot."""

class INVALID_REQ (Exception):
    """Request is invalid."""

class INVALID_PAR (Exception):
    """Request parameters is invalid."""

class NEED_OWN (Exception):
    """You need to claim ownership before running this function."""

CLIENT_EXCEPTION = (NO_CONNECTION, NEED_OWN, FAILED, SocketTimeout, INVALID_PAR, INVALID_REQ)

###########
### AUX ###
###########
def get_client(client_id: str, *, timeout: int = 3000) -> _zmq.Socket:
    """Get a client for the server using client_id, and timeout (in milliseconds)."""
    return _get_client(_config.SERVER_SOCKET, client_id, timeout=timeout)



def raise_client_errors(server_reply: bytes) -> str:
    """Raise errors based on server response. Also decodes values, for convenience ;)."""
    server_reply_body = b'\n'.join(server_reply.split(b'\n')[1:])
    match(server_reply_body):
        case _config.Response.FAILED:
            raise FAILED

        case _config.Response.NO_CONNECTION:
            raise NO_CONNECTION

        case _config.Response.INVALID_PAR:
            raise INVALID_PAR

        case _config.Response.NEED_OWN:
            raise NEED_OWN

        case _config.Response.INVALID_REQ:
            raise INVALID_REQ

        case _:
            return server_reply_body.decode('utf-8')


##############
### CLIENT ###
##############
class Team_11_Client:
    Timeout = SocketTimeout

    def __init__(self, identifier: str, request_timeout: int = 3000):
        self._id     = identifier
        self._client = get_client(identifier, timeout=request_timeout)

    @staticmethod
    def _hex(val: str | bytes) -> int:
        """Translate hex input to an integer."""
        if isinstance(val, str | bytes):
            return ord(val)
        return val


    def _send(self, msg: bytes) -> None:
        print(f"[{self._id}] Sending messagee: {msg}")
        self._client.send(msg) ## Send to actual "client" socket


    def claim_ownership(self) -> None:
        """Claim ownership, for access to movement and rotate and stop commands."""
        self._send( _config.Command.CLAIM_OWN )
        _ = raise_client_errors(self._client.recv())
        return



    def move_forward(self, distance: float) -> float:
        """Send move forward command, returns movement from last movement commad."""
        self._send( _config.Command.MOVE_FORWARD + f'\n{distance}'.encode('utf-8') )
        reply = raise_client_errors(self._client.recv())
        return float(reply)



    def rotate(self, angle: float) -> None:
        """Send rotate command."""
        self._send( _config.Command.ROTATE + f'\n{angle}'.encode('utf-8') )
        _ = raise_client_errors(self._client.recv())
        return



    def stop(self) -> float:
        """Stop robot."""
        self._send( _config.Command.STOP )
        reply = raise_client_errors(self._client.recv())
        return float(reply)



    def is_active(self) -> bool:
        """Check if robot is moving."""
        self._send( _config.Command.IS_ACTIVE )
        reply = raise_client_errors( self._client.recv() )
        return bool(int(reply))



    def progress(self) -> float:
        """Returns progress, in inches, along last move."""
        self._send( _config.Command.GET_PROGRESS )
        reply = raise_client_errors( self._client.recv() )
        return float(reply)



    def led(self, r: int | bytes | str, g: int | bytes | str, b: int | bytes | str) -> None:
        """Set LED on robot. Value inputs in range [0, 255]."""
        ## Typecase r, g, b to <int>
        r = self._hex(r)
        g = self._hex(g)
        b = self._hex(b)

        ## Send LED command
        self._send( _config.Command.LED + f'\n{r}\n{g}\n{b}'.encode('utf-8') )
        _ = raise_client_errors(self._client.recv())
        return



    def led_off(self) -> None:
        """Set LED to OFF."""
        self._send( _config.Command.LED_OFF )
        _ = raise_client_errors(self._client.recv())
        return



    def ultrasonic(self) -> list[float]:
        """Get inch readings for values."""
        self._send( _config.Command.ULTRASONIC )
        reply = raise_client_errors(self._client.recv())
        print("Reply: ", reply)
        return _json_loads(reply)



    def ultrasonic_json(self, measurment_count: int) -> dict[str, list[float]]:
        """Return json with lists of inch readings from ultrasonic sensors."""
        self._send( _config.Command.ULTRASONIC_TABLE + f'\n{measurment_count}'.encode('utf-8') )
        reply = raise_client_errors(self._client.recv())
        return _json_loads(reply)


