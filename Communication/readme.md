# API....
``` python

## Option 1
from robot_server import Team_11_Client
robot = Team_11_Client('Master')

## Option 2
from robot_direct import Team_11_Client
robot = Team_11_Client('COM13')




## If using robot_server, run following line
robot.claim_ownership()

try:
    ...
except ( NO_CONNECTION, INVALID_REQUEST, INVALID_PARAMS, FAILED, NO_OWNERSHIP ):
    ...

## REQUIRE OWNERSHIP
try:
    robot.move_forward(inches_fwd) # -> float distance_on_last
    robot.rotate(angle_clockwise) # -> None
    robot.stop() # -> float distance_on_last

except NO_OWNERSHIP:
    robot.claim_ownership()
    ... try again ...

robot.is_active() # -> bool is_active
robot.progress() # -> float distance_on_last

robot.led(r, g, b) # -> None
robot.led_off() # -> None

robot.ultrasonic() # -> list[ultrasonic_readings] [u0, u1, u2, u3, u4, u5]
robot.ultrsaonic_json(number_of_attempts) # -> json[] -> {'u0': [read_1, read_2, ...]}
```
