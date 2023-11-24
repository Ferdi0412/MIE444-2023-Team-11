from time import sleep

from robot_direct import Team_11_Client

robot = Team_11_Client("COM13")


robot.move_forward(10)

while robot.is_active():
    sleep(0.5)
