"""Make requests to robot..."""
######################
### BASE LIBRARIES ###
######################
import serial as _serial

#########################
### CUSTOMM LIBRARIES ###
#########################


##################
### EXCEPTIONS ###
##################
class NoAcknowledge (Exception):
    """Raised when acknowledge is not received."""

class NoReply (Exception):
    """Raised when reply format is never received."""


########################
### PUBLIC FUNCTIONS ###
########################
def wait_for_acknowledge(serial_: _serial.Serial, ack_msg: bytes, retries: int = None) -> None:
    """Raises NoAcknowledge."""
    for _ in range(retries or 1):
        if serial_.readline().replace(b'\n', b'').replace(b'\r', b''):
            return
    raise NoAcknowledge



def wait_for_reply(serial_: _serial.Serial, msg_prefix: bytes, retries: int = None) -> None:
    """Raises NoReply."""
    prefix_len = len(msg_prefix)
    for _ in range(retries or 1):
        msg = serial_.readline()
        if msg_prefix == msg[:prefix_len]:
            return msg
    raise NoReply

def wait_for_replies(serial_: _serial.Serial, msg_options: list[bytes], retries: int = None) -> bytes:
    """Raises NoReply."""
    for _ in range(retries or 1):
        msg = serial_.readline()
        if msg.replace(b'\n', b'').replace(b'\r', b'') in msg_options:
            return msg
    raise NoReply
