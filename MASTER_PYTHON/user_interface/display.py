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

    @staticmethod
    def go_manual(state: bool):
        raise NotSetup

    @staticmethod
    def localize_global():
        raise NotSetup

    @staticmethod
    def localize_oneoff():
        raise NotSetup

    @staticmethod
    def path_to_loading_zone():
        raise NotSetup

    @staticmethod
    def path_to_location():
        raise NotSetup

    @staticmethod
    def manual_path():
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
            RobotController.go_manual(True)
            manual_mode = True

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_0:
            RobotController.go_manual(False)
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

            # elif event.key == pygame.K_u:
            #     RobotController.ultrasonic()

            elif event.key == pygame.K_u:
                RobotController.localize_oneoff()

            elif event.key == pygame.K_6:
                RobotController.localize_global()

            elif event.key == pygame.K_n:
                RobotController.path_to_loading_zone()

            elif event.key == pygame.K_m:
                RobotController.path_to_location()

            elif event.key == pygame.K_b:
                RobotController.manual_path()

        elif manual_mode and event.type == pygame.KEYUP and event.key in (pygame.K_w, pygame.K_s, pygame.K_q, pygame.K_e):
            RobotController.stop()

    keys_pressed = pygame.key.get_pressed()
    clockwise = keys_pressed[pygame.K_e] - keys_pressed[pygame.K_q]

    if manual_mode and clockwise > 0:
        RobotController.go_clockwise(ROT_DIST)

    elif manual_mode and clockwise < 0:
        RobotController.go_clockwise(-ROT_DIST)



def draw():
    clock.tick(FPS)

    handle_input()

    screen.fill(WHITE if manual_mode else NEUTRAL_BG)

    robot.draw(screen, text_font)

    pygame.display.flip()



def daemon():
    while True:
        draw()



def register_robot(robot):
    global RobotController
    RobotController.go_fwd       = robot.move_forward
    RobotController.go_clockwise = robot.rotate
    RobotController.led          = robot.led
    RobotController.led_off      = robot.led_off
    RobotController.stop         = robot.stop



def register_ultrasonic(ultrasonic_readings: dict):
    """Register a set of ultrasonic values."""
    global robot
    robot.append(ultrasonic_readings)



def register_ultrasonic_json(ultrasonic_json: dict):
    global robot
    robot.extend(ultrasonic_json)



if __name__ == '__main__':
    daemon()
