###############
### MODULES ###
###############
import pygame as _pygame
import sys    as _sys
import os     as _os


######################
### CUSTOM MODULES ###
######################
_sys.path.append(_os.path.dirname(__file__))
from _cfg import ROBOT_FILL, BLACK, WHITE, X0, Y0, PIXEL_SCALE
_=_sys.path.pop()



#############
### CLASS ###
#############
class RobotGraphic:
    def __init__(self, pygame_ref, outline, ultrasonic_sensors: dict = None):
        self._pygame = pygame_ref
        self._outline = outline
        self._sensors = ultrasonic_sensors
        self._theta   = 0

    @property
    def outline(self) -> list[float]:
        ## Apply theta trans
        return [(x * PIXEL_SCALE + self.cx,
                 y * PIXEL_SCALE + self.cy,)
                for x, y in self._outline]

    @property
    def cx(self) -> float:
        return X0

    @property
    def cy(self) -> float:
        return Y0

    def set_theta(self, theta):
        self._theta = theta
        return self



    def set_sensors(self, ultrasonic_sensors: dict):
        self._sensors = ultrasonic_sensors
        return self



    def draw(self, screen: _pygame.Surface, text: _pygame.font.SysFont = None) -> None:
        self._pygame.draw.polygon(screen, ROBOT_FILL, self.outline, 0)

        if self._sensors:
            for sid, sensor in self._sensors.items():
                sensor.draw(screen)

                if text:
                    sensor.display_text(screen, text, sensor.cx + 5, sensor.cy + 5)

            # if text:
            #     front_diff = self._sensors['FR'].latest() - self._sensors['FL'].latest()
            #     txt_       = text.render(f"{front_diff:.1f}", True, BLACK, WHITE)
            #     txt_rect   = txt_.get_rect(center=(self.cx, self.cy))
            #     screen.blit(txt_, txt_rect)



    def append(self, ultrasonic_readings: dict) -> None:
        for sensor_id, sensor_value in ultrasonic_readings.items():
            if sensor_id in self._sensors:
                self._sensors[sensor_id].append(sensor_value)
        return self



    def extend(self, ultrasonic_readings: dict) -> None:
        for sensor_id, sensor_value in ultrasonic_readings.items():
            if sensor_id in self._sensors:
                self._sensors[sensor_id].extend(sensor_value)
        return self
