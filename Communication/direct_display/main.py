###############
### MODULES ###
###############

import pygame

import os  as _os
import sys as _sys

######################
### CUSTOM MODULES ###
######################
_sys.path.append(_os.path.dirname(__file__))
from _cfg import get_robot_config, PIXEL_SCALE
_=_sys.path.pop()

#############
### SETUP ###
#############
_cfg = get_robot_config()
robot_outline = [(x * PIXEL_SCALE + X0, y * PIXEL_SCALE + Y0) for x, y  in _cfg['outline']]

