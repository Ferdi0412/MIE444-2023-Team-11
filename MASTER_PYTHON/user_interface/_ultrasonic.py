###############
### MODULES ###
###############
import math   as _math
import numpy  as _numpy
import pygame as _pygame
import os     as _os
import sys    as _sys

from collections import deque as _deque
# import pygame.math



######################
### CUSTOM MODULES ###
######################
_sys.path.append(_os.path.dirname(__file__))
from _cfg import PIXEL_SCALE, X0, Y0, RAY_COL, RAY_AVG_COL
_=_sys.path.pop()




##############
### CONFIG ###
##############
SHOW_AVG   = True
AVG_RADIUS = 1
STEPS      = 6
D_ALPHA    = _math.radians(5 / (STEPS * 2))
BUFFER_LEN = 8


#############
### CLASS ###
#############
class UltrasonicSensor:
    def __init__(self, cx: int, cy: int, rot: float, ):
        self._theta    = 0
        self._x0       = X0
        self._y0       = Y0
        self._cx       = cx
        self._cy       = cy
        self._rot      = _math.radians(rot)
        self._buffer   = _deque([0], BUFFER_LEN)



    @property
    def cx(self) -> float:
        """Calculate position of sensor based on given theta orientation."""
        return self._x0 + (_math.sin(self._theta) * self._cy + _math.cos(self._theta) * self._cx) * PIXEL_SCALE

    @property
    def cy(self) -> float:
        """Calculate position of sensor based on given theta orientation."""
        return self._y0 + (_math.sin(self._theta) * self._cx + _math.cos(self._theta) * self._cy) * PIXEL_SCALE

    @property
    def txt(self) -> str:
        """Return string of latest reating."""
        return f"{self.latest() % 12:.1f}+{self.latest() // 12:.0f}"

    def set_x0(self, x0):
        self._x0 = x0
        return self

    def set_y0(self, y0):
        self._y0 = y0
        return self

    def set_theta(self, theta):
        self._theta = _math.radians(theta)
        return self



    def draw(self, screen: _pygame.Surface) -> None:
        ## Draw "main" ray
        dist   = self.latest() * PIXEL_SCALE
        cx     = self.cx # self.cx
        cy     = self.cy # self.cy
        rot    = self._rot

        ## If SHOW AVERAGE
        if SHOW_AVG:
            mean = self.mean() * PIXEL_SCALE

        ## Project rays
        for ray_i in range(-STEPS, STEPS+1):
            alpha = rot + ray_i * D_ALPHA
            x     = cx + dist * _math.sin(alpha) # + theta
            y     = cy + dist * _math.cos(alpha) # + theta
            _pygame.draw.line(screen, RAY_COL, (cx, cy,), (x, y,))

            ## Display average if SHOW AVERAGE
            if SHOW_AVG:
                ax = cx + mean * _math.sin(alpha) # + theta
                ay = cy + mean * _math.cos(alpha) # + theta
                _pygame.draw.circle(screen, RAY_AVG_COL, (ax, ay,), AVG_RADIUS)



    def display_text(self, screen: _pygame.Surface, text: _pygame.font.SysFont, txt_x: int, txt_y: int) -> None:
        txt_val  = self.txt.encode('utf-8')
        txt_     = text.render(txt_val, True, (0, 0, 0,), (255, 255, 255,))
        txt_rect = txt_.get_rect(center = (txt_x, txt_y,))
        screen.blit(txt_, txt_rect)



    def latest(self) -> float:
        """Return latest appended value."""
        return self._buffer[0]

    def append(self, value: float) -> None:
        """Append a reading to the buffer."""
        self._buffer.appendleft(value)

    def extend(self, value: list[float]) -> None:
        """Extend readings to the buffer."""
        self._buffer.extendleft(value)

    def mean(self) -> float:
        """Return mean of sensor readings in buffer."""
        return _numpy.mean(self._buffer)
