from connector.sender import Team_11_Robot

import time

robot = Team_11_Robot("COM13", 2000)

robot.move_forward(-3)
print(robot.is_active())
print(robot.progress())

while robot.is_active():
    time.sleep(0.1)
    print("Waiting")

robot.move_forward(3)
print(robot.ultrasonic_json(5))

time.sleep(1)
print(robot.is_active())
print(robot.progress())
