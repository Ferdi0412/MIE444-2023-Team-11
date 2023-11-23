"""Handles communication to-and-from robot."""
import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from _socket import get_client, SocketTimeout


def get_ultrasonics():
    return []

def _is_active() -> bool:
    return False

def fwd() -> None:
    if _is_active():
        return

def init():
    global CLIENT
    CLIENT = get_client('Manual-Interface')
