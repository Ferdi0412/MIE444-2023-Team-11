"""Package for working with Team 11's robot."""

from .control_robot import NoMotorAck, SingleMotorAck, NoUltrasonics, Team_11_Robot
from .server_client import get_client, Team_11_Client

## Expose local stuff
# import sys as _sys, os as _os; _sys.path.append(_os.path.dirname(__file__))
#
# from control_robot import NoMotorAck, SingleMotorAck, NoUltrasonics, Team_11_Robot
#
# _ = _sys.path.pop()

__all__ = ['NoMotorAck', 'SingleMotorAck', 'NoUltrasonics', 'Team_11_Robot', 'get_client', 'Team_11_Client']
