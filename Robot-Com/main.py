"""Running some stuff against the robot...."""
#COM = "COM13"

##############
### IMPORT ###
##############
import time

## Expose robot class
import sys, os; sys.path.append(os.path.dirname(__file__))

from robot import NoMotorAck, SingleMotorAck, NoUltrasonics, Team_11_Robot

import numpy, pandas

_ = sys.path.pop()



############
### MAIN ###
############
if __name__ != '__main__':
    exit()


# df = pandas.DataFrame([], columns=['u0', 'u1', 'u2', 'u3', 'u4', 'u5'])

# def get_us_df_multirow(num_readings: int, delay_: float = None):
#     df = pandas.
#     df = pandas.DataFrame([], columns=['u0', 'u1', 'u2', 'u3', 'u4', 'u5'])
#     print(df)
#     for _ in range(num_readings):
#         new_df = pandas.DataFrame(robot.get_ultrasonics(), columns=['u0', 'u1', 'u2', 'u3', 'u4', 'u5'])
#         print(new_df)
#         df = pandas.concat(None, new_df)
#     return df
    #df.append(robot.get_ultrasonics())


robot = Team_11_Robot("COM13")

# print("Getting ultrasonics 5 times!")

# print(get_us_df().to_json())

# print(robot.get_ultrasonics())

print(robot.stop())
print(robot.move_forward(10))

print(robot.get_ultrasonics_DataFrame(4))

input("[ENTER] to stop...\n")
print(robot.stop())
# time.sleep(0.5)
# print(robot.move_forward(10, 60))
# time.sleep(0.5)
# print(robot.stop())
# time.sleep(0.5)
# print(robot.rotate(10))
# print(robot.move_forward(10))
# print(robot.get_active())
# time.sleep(0.5)
# print(robot.stop())
