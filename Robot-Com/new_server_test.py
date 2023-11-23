from robot import Team_11_Client
import time

robot = Team_11_Client("Test")

robot.claim_ownership()

print(robot.rotate(180))

while ( robot.is_active() ):
    time.sleep(0.5)

# print(robot.stop())

# robot.led('\x00', '\xFF', '\xAA')

# print(robot.progress())

# time.sleep(2)

# robot.led_off()

# print(robot.ultrasonic())

# print(robot.ultrasonic_json(5))

# print(robot.is_active())

# print(robot.progress())
