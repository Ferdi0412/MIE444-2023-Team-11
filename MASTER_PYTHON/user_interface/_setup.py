####################
### BASE MODULES ###
####################
import pygame
import sys
import os
import time

######################
### CUSTOM MODULES ###
######################
sys.path.append(os.path.dirname(__file__))
from _cfg        import *
from _robot      import RobotGraphic
from _ultrasonic import UltrasonicSensor

############
### MAIN ###
############
CONFIG        = get_robot_config()
ROBOT_OUTLINE = CONFIG['outline']
FPS           = 20

LIN_DIST = 10
ROT_DIST = 10

LED_COLS = [[b'\x55', b'\x00', '\xCC'],
            [b'\x99', b'\x20', b'\xFE'],
            [b'\x00', b'\x33', b'\x66'],
            [b'\x00', b'\xFF', b'\xFF']]
LED_IDX  = 0

clock         = pygame.time.Clock()
screen        = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
text_font     = None

manual_mode   = False

class NotSetup(Exception):
    """Please assign this function!"""

class RobotController:
    @staticmethod
    def go_fwd(dist):
        raise NotSetup

    @staticmethod
    def go_clockwise(angle):
        raise NotSetup

    @staticmethod
    def stop():
        raise NotSetup

    @staticmethod
    def led(r, g, b):
        raise NotSetup

    @staticmethod
    def led_off():
        raise NotSetup

    @staticmethod
    def ultrasonic():
        raise NotSetup


## TODO: Find some implementation for this
ultrasonics   = {sensor_id: UltrasonicSensor(val['location'][0], val['location'][1], val['rotation']) for sensor_id, val in CONFIG['ultrasonic'].items()}
# ultrasonics   = {'a': UltrasonicSensor(0, 0, 20)}

robot = RobotGraphic(pygame, ROBOT_OUTLINE, ultrasonics)

def init():
    global text_font
    pygame.init()
    text_font = pygame.font.SysFont("Times New Roman", 18)
    print("Pygame [init]...")
    print("""Key bindings:
<.> -> Go Manual
<0> -> Go Automatic
<w> -> Go Forward
<s> -> Go Backwards
<e> -> Rotate Clockwise
<q> -> Rotate Counter-Clockwise
<x> -> STOP
<l> -> LED-ON (white)
<p> -> LED-OFF
          """)

def handle_input():
    global manual_mode
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_PERIOD:
            manual_mode = True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
            manual_mode = False

        elif manual_mode and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_l:
                global LED_IDX
                RobotController.led(*LED_COLS[LED_IDX]) # TURN LED ON
                LED_IDX = 0 if (LED_IDX + 1 >= len(LED_COLS)) else LED_IDX + 1

            elif event.key == pygame.K_p:
                RobotController.led(0, 0, 0) # TURN LED OFF

            elif event.key == pygame.K_w:
                RobotController.go_fwd(LIN_DIST)

            elif event.key == pygame.K_s:
                RobotController.go_fwd(-LIN_DIST)

            elif event.key == pygame.K_u:
                RobotController.ultrasonic()

            # elif event.key == pygame.K_e:
            #     RobotController.go_clockwise(ROT_DIST)

            # elif event.key == pygame.K_q:
            #     RobotController.go_clockwise(-ROT_DIST)

        elif manual_mode and event.type == pygame.KEYUP:
            RobotController.stop()

    keys_pressed = pygame.key.get_pressed()

    # fwd       = keys_pressed[pygame.K_w] - keys_pressed[pygame.K_s]
    clockwise = keys_pressed[pygame.K_e] - keys_pressed[pygame.K_q]
    # # right     = keys_pressed[pygame.K_d] - keys_pressed[pygame.K_a]
    # stop      = keys_pressed[pygame.K_x]
    # go_manual = keys_pressed[pygame.K_PERIOD]
    # go_auto   = keys_pressed[pygame.K_0]

    # if go_manual:
    #     manual_mode = True
    #     pass

    # elif go_auto:
    #     manual_mode = False
    #     pass

    # elif manual_mode and stop:
    #     RobotController.stop()

    # elif manual_mode and fwd > 0:
    #     RobotController.go_fwd(LIN_DIST)

    # elif manual_mode and fwd < 0:
    #     RobotController.go_fwd(-LIN_DIST)

    if manual_mode and clockwise > 0:
        RobotController.go_clockwise(ROT_DIST)

    elif manual_mode and clockwise < 0:
        RobotController.go_clockwise(-ROT_DIST)

    # elif manual_mode:
        # RobotController.stop()

def draw():
    clock.tick(FPS)

    handle_input()

    screen.fill(WHITE if manual_mode else NEUTRAL_BG)

    robot.draw(screen, text_font)

    pygame.display.flip()

def daemon():
    while True:
        draw()

if __name__ == '__main__':
    daemon()
