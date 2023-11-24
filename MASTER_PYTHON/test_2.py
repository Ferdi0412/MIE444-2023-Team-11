import sys, os; sys.path.append(os.path.dirname(__file__));

from connector.sender import Team_11_Robot, _serial

import time

# import serial

robot = Team_11_Robot("COM13", 2)
# robot = _serial.Serial("COM10", timeout=None)

robot.move_forward(3)

# robot.led(0, 255, 255)

# robot.rotate(45)

# robot.move_forward(-3)
# print(robot.is_active())
# print(robot.progress())

# while robot.is_active():
#     time.sleep(0.1)
#     print("Waiting")

# time.sleep(0.2)

# robot.move_forward(3)
# print(robot.ultrasonic_json(5))

# time.sleep(1)
# print(robot.is_active())
# print(robot.progress())
