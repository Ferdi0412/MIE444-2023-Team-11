"""Running some stuff against the robot...."""
#COM = "COM13"

##############
### IMPORT ###
##############
import time

## Expose robot class
import sys, os; sys.path.append(os.path.dirname(__file__))

from robot import NoMotorAck, SingleMotorAck, NoUltrasonics, Team_11_Robot

_ = sys.path.pop()



############
### MAIN ###
############
if __name__ != '__main__':
    exit()





robot = Team_11_Robot("COM13")

print(robot.stop())
print(robot.move_forward(10))
time.sleep(0.5)
print(robot.stop())
time.sleep(0.5)
print(robot.rotate(10))
print(robot.get_active())
time.sleep(0.5)
print(robot.stop())
