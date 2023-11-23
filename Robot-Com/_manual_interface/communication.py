"""Handles communication to-and-from robot."""
import time as _time

######################
### CUSTOM IMPORTS ###
######################
import sys, os; sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from robot import Team_11_Client, NEED_OWN, CLIENT_EXCEPTION

_ = sys.path.pop()


#########################
### CRAY-CRAY-WRAPPER ###
#########################
def handle_man_mode(og_function):
    def handle_err(*args, **kwargs):
        global MANUAL_MODE
        if MANUAL_MODE:
            try:
                og_function(*args, **kwargs)
            except NEED_OWN:
                MANUAL_MODE = False
            except CLIENT_EXCEPTION:
                return
    return handle_err



############
### MAIN ###
############
client = Team_11_Client("Manual-Interface", request_timeout=10000)

MANUAL_MODE = False

def get_ultrasonics():
    return client.ultrasonic()

def enter_manual_mode():
    global MANUAL_MODE
    MANUAL_MODE = True
    client.claim_ownership()

# def _is_active() -> bool:
#     return False

def in_manual_mode():
    return MANUAL_MODE

@handle_man_mode
def fwd() -> None:
    client.move_forward(0.5)
    _time.sleep(0.1)

@handle_man_mode
def bwd() -> None:
    client.move_forward(-0.5)
    _time.sleep(0.1)

@handle_man_mode
def clockwise() -> None:
    client.rotate(5)
    _time.sleep(0.1)

@handle_man_mode
def counter_clockwise() -> None:
    client.rotate(-5)
    _time.sleep(0.1)
