###############
### MODULES ###
###############
import os    as _os
import sys   as _sys

######################
### CUSTOM MODULES ###
######################

_sys.path.append(_os.path.dirname(_os.path.dirname(__file__)))
from connector.sender import Team_11_Robot
# from automation._localization import predict_location, predict_first_location
# _=_sys.path.pop()

############
### MAIN ###
############
robot = Team_11_Robot("COM13", 2)

robot.led(255, 255, 255)
