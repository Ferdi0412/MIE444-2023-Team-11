class Message:
    MOVE_FORWARD    = b'MOVE-FORWARD'
    ROTATE          = b'ROTATE'
    STOP            = b'STOP'
    GET_ACTIVE      = b'GET-ACTIVE'
    GET_PROGRESS    = b'GET-PROGRESS'
    SET_LED         = b'SET-LED'
    SET_LED_OFF     = b'SET-LED-OFF'
    GET_ULTRASONICS = b'GET-ULTRASONICS'
    IS_OWNER        = b'IS-OWNER'
    GET_OWNERSHIP   = b'GET-OWNERSHIP'

class Failed (Exception):
    """Raised when a request failed..."""

class Invalid (Exception):
    """Raised when a request for something that does not exist occurs..."""

class FatalError (Exception):
    """Raised when an uncaught error occured..."""
