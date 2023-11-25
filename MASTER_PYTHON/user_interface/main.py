###############
### MODULES ###
###############

import time

import os    as _os
import sys   as _sys
import numpy as _numpy

######################
### CUSTOM MODULES ###
######################
_sys.path.append(_os.path.dirname(__file__))
import _setup
import _cfg
_=_sys.path.pop()

_sys.path.append(_os.path.dirname(_os.path.dirname(__file__)))
from connector.sender import Team_11_Robot
from automation._localization import predict_location, predict_first_location
_=_sys.path.pop()

#############
### SETUP ###
#############
_setup.init()

_setup.FPS      = 40
_setup.LIN_DIST = 10
_setup.ROT_DIST = 15

robot = Team_11_Robot("COM12", 2)

_setup.RobotController.go_fwd       = robot.move_forward
_setup.RobotController.go_clockwise = robot.rotate
_setup.RobotController.led          = robot.led
_setup.RobotController.led_off      = robot.led_off
_setup.RobotController.stop         = robot.stop
_setup.RobotController.ultrasonic   = lambda: print(predict_first_location(_numpy.array(list(robot.ultrasonics().values()))))

while True:
    _setup.robot.append(robot.ultrasonics())
    _setup.draw()
