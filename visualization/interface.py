import os, sys; sys.path.append(os.path.dirname(__file__));

from serial_functions import *

import pygame
import yaml
import time
import math
from numbers import Number

# Define a function to load the YAML configuration
def get_cfg(file_name):
    with open(file_name, 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    return cfg

# Load the configuration from the YAML file
cfg = get_cfg(os.path.dirname(__file__) + '/config.yaml')

# Initialize Pygame
pygame.init()

text_font = pygame.font.SysFont("Times New Roman", 18)



# Create the Pygame screen with dimensions from the configuration
screen = pygame.display.set_mode((cfg['screen-width'], cfg['screen-height']))

x0 = cfg['screen-width'] / 2
y0 = cfg['screen-height'] / 2

# Define colors from the configuration
bg_col        = cfg['background-color']
robot_col     = cfg['robot-color']
us_col        = cfg['ultrasonic-color']
px_scale      = cfg['pixel-scale']
avg_col       = cfg.get('average-color', None)
avg_size      = cfg.get('average-draw-sz', 0.5)
robot_outline = [(x * px_scale + x0, y * px_scale + y0)
                 for x, y in cfg['robot-outline']]
wheel_outline = pygame.Rect([coord * px_scale for coord in cfg['wheel-outline']])
us_scale      = cfg['ultrasonic-scale']
wheel_col     = cfg['wheel-color']

# Create a Pygame clock
clock = pygame.time.Clock()

print(robot_outline)

class UltrasonicSensor:
    def __init__(self, params: dict):
        self._params: dict     = params
        self._location: tuple  = params['location']
        self._rotation: Number = math.radians(params['rotation'])
        self._steps: int       = (params.get('steps', 6) // 2)
        self._angle: float     = (math.radians(params.get('angle', 5)) / (2 * self._steps ))
        self._buffer_len: int  = params.get('buffer-len', 20)
        self._buffer: list     = [1] * self._buffer_len
        self._draw_mean: bool  = params.get('draw_mean', False)

    def draw(self):
        dist = self.latest() * px_scale
        cx   = x0 + px_scale * self._location[0]
        cy   = y0 + px_scale * self._location[1]
        rot  = self._rotation
        if avg_col:
            avg = self.avg() * px_scale
        for step in range(-self._steps, self._steps + 1):
            angle = self._angle * step
            ex = cx + dist * math.sin(rot - angle)
            ey = cy + dist * math.cos(rot - angle)
            pygame.draw.line(screen, us_col, (cx, cy,), (ex, ey,))
            if avg_col:
                ex = cx + avg * math.sin(rot - angle)
                ey = cy + avg * math.cos(rot - angle)
                pygame.draw.circle(screen, avg_col, (ex, ey,), avg_size)



    def append(self, value: float):
        _ = self._buffer.pop(0)
        self._buffer.append(value * us_scale)

    def latest(self) -> float:
        return self._buffer[-1]

    def avg(self) -> float:
        return sum(self._buffer) / len(self._buffer)

ultrasonics = {name: UltrasonicSensor(value) for (name, value) in cfg['ultrasonic'].items()}

print("Enterring main....")

while True:
    clock.tick(60)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                forward()

            if event.key == pygame.K_s:
                backward()

            if event.key == pygame.K_a:
                left()

            if event.key == pygame.K_d:
                right()

            if event.key == pygame.K_q:
                clockwise()

            if event.key == pygame.K_e:
                counterclockwise()

    # Clear the screen with the background color
    screen.fill(bg_col)

    # Draw the robot's outline
    pygame.draw.rect(screen, wheel_col, wheel_outline)
    pygame.draw.polygon(screen, robot_col, robot_outline, 0)

    # Draw ultrasonic sensor representations
    newest_readings = get_ultrasonics()
    for i, us in enumerate(ultrasonics.values()):
        us.append(newest_readings[i])
        us.draw()

    # Update the display
    pygame.display.flip()


    # Optional: You may want to add logic here to update your screen based on signals and values

