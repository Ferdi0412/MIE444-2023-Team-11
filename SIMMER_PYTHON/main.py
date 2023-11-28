import time
import numpy
import math



from connector import Team_11_Robot
from maze import histogram, pathfind
import user_interface.display as display

#####################
### GLOBAL PARAMS ###
#####################
FR_BR = 4 ## Distance from front right and back right sensors
FL_BL = 4 ## Distance from front left and back left sensors

RIGHT_FROM_CENTER = 2.6
LEFT_FROM_CENTER  = 2.6
FRONT_FROM_CENTER = 3.2
BACK_FROM_CENTER  = 3.2

## == MAIN ==
COM_PORT = "COM10"

MANUAL_MODE = False

## == DISPLAY ==
display.FPS = 15
## Distances travelled per "press" in manual mode
display.LIN_DIST = 10
display.ROT_DIST = 15

## Enable display to trigger "MANUAL_MODE"
def _go_manual(state: bool):
    global MANUAL_MODE
    MANUAL_MODE = state
display.RobotController.go_manual = _go_manual

print(display.ultrasonics.keys())

#############
### SETUP ###
#############
print("[Team_11_Robot] is getting set up")
robot = Team_11_Robot(COM_PORT, 2)

print("[display] is getting set up")
display.register_robot(robot)
display.init()
# display_thread = Thread(target = display.daemon, daemon=True)

print("[histogram] is getting set up")
histogram.DISTANCE_THRESHOLD = 2
histogram.setup()

print("SETUP COMPLETE!", end='\n\n')

##################
### OPERATIONS ###
##################
class Stuck (Exception):
    pass


ROTATE_ERR       = 1.05
ANGLE_THRESHOLD  = 8
ALIGN_RETRIES    = 10
MOVE_INCREMENTS  = 1

LATEST_ULTRASONICS = None


def get_ultrasonics():
    global LATEST_ULTRASONICS
    readings = robot.ultrasonics()
    display.register_ultrasonic(readings)
    LATEST_ULTRASONICS = readings
    return readings



def pass_time(sleep_s: int = 0.1):
    display.register_ultrasonic(robot.ultrasonics())
    time.sleep(sleep_s)



def rotate(angle: int):
    robot.rotate(angle)
    while robot.is_active():
        pass_time(0.05)



def move(distance_fwd: float):
    robot.move_forward(distance_fwd)
    while robot.is_active():
        pass_time(0.05)



## Not a good approach
# def move_safe(distance_fwd: float):
#     """Same as move, but checks that front sensor reading is changing over duration."""
#     initial_reading = get_ultrasonics()['F']
#     move(distance_fwd)
#     final_reading   = get_ultrasonics()['F']
#     delta_reading = initial_reading - final_reading
#     if delta_reading > ((1+MOVE_FORWARD_ERR) * distance_fwd) or delta_reading < ((1-MOVE_FORWARD_ERR) * distance_fwd):
#         raise Stuck(f"Expected to move {distance_fwd}, only moved {delta_reading}. {(1 - delta_reading / distance_fwd) * 100:.2f}% ERR.")



def left_angle(avg_over: int = 1) -> float:
    """Angle clockwise. Ie. if value is positive, will move away from left wall in positive direction."""
    measured = []
    for _ in range(avg_over or 1):
        ultrasonics = get_ultrasonics()
        measured.append(math.degrees(math.atan((ultrasonics['FL'] - ultrasonics['BL']) / FR_BR)))
    return numpy.mean(measured)

def left_align(offset: int = 0) -> None:
    """Align wall based off of left sensors, no large turns, just minor adjustments. Only targets parallel."""
    ## alpha is positive clockwise from wall in front of robot...
    alpha = left_angle(3) - offset
    for _ in range(ALIGN_RETRIES):
        if abs(alpha) <= ANGLE_THRESHOLD:
            return
        ## Adjustment should be reduced by half of alpha, in case of overshoot. Better to move several times
        adjustment = math.copysign(abs(alpha) - (ANGLE_THRESHOLD / 2), alpha)
        print(f"Making left-align adjustment of {adjustment} degrees.")
        rotate(adjustment)
        alpha = left_angle() - offset

def left_parallel(offset: int = 0) -> bool:
    return abs(left_angle() - offset) < ANGLE_THRESHOLD

def move_left_parallel(distance_fwd) -> None:
    """Move whilst trying to keep parallel to the left-side wall."""
    steps = distance_fwd // MOVE_INCREMENTS
    left_align()
    for _ in range(steps):
        move(MOVE_INCREMENTS)
        ## Adjust a little extra to either side, to account for minor drifts
        left_align(-left_angle() / 2)
    move(distance_fwd % MOVE_INCREMENTS)

def dist_from_left_wall() -> float | None:
    """Returns distance from center of robot"""
    if not left_parallel():
        return None
    return ( LATEST_ULTRASONICS['FL'] + LATEST_ULTRASONICS['BL'] ) / 2 + LEFT_FROM_CENTER


def blocks_from_left_wall() -> float | int | None:
    """Returns blocks from center of robot to left wall"""
    dist = dist_from_left_wall()
    if dist is None:
        return None
    return ((dist) // 3) / 4




def right_angle(avg_over: int = 1) -> float:
    """Angle clockwise. Ie. if value is positive, will move towards wall on right side in positive direction."""
    measured = []
    for _ in range(avg_over or 1):
        ultrasonics = get_ultrasonics()
        measured.append(math.degrees(math.atan((ultrasonics['BR'] - ultrasonics['FR']) / FR_BR)))
    return numpy.mean(measured)

def right_align(offset: int = 0) -> None:
    """Calculate angle based off two right-side-sensors."""
    ## alpha is positive clockwise from wall in front of robot...
    alpha = right_angle(3) - offset
    for _ in range(ALIGN_RETRIES):
        if abs(alpha) <= ANGLE_THRESHOLD:
            return
        ## Adjustment should be reduced by half of alpha, in case of overshoot. Better to move several times.
        adjustment = math.copysign(abs(alpha) - (ANGLE_THRESHOLD / 2), alpha)
        print(f"Making right-align adjustment of {adjustment} degrees.")
        rotate(adjustment)
        alpha = right_angle() - offset

def right_parallel(offset: int = 0) -> bool:
    return abs(right_angle() - offset) <= ANGLE_THRESHOLD

def dist_from_right_wall() -> float | None:
    """Returns distance from center of robot"""
    if not right_parallel():
        return None
    return ( LATEST_ULTRASONICS['FR'] + LATEST_ULTRASONICS['BR'] ) / 2 + RIGHT_FROM_CENTER

def blocks_from_right_wall() -> float | int | None:
    """Returns blocks from center of robot to left wall"""
    dist = dist_from_right_wall()
    if dist is None:
        return None
    return ((dist) // 3) / 4

def move_right_parallel(distance_fwd, right_dist: int = None) -> None:
    """Move whilst trying to keep parallel to the right-side wall."""
    ## TODO: Figure out how to implement offset to re-center robot (if necessary).
    ## Solution for running without progress -> otherwise have a while robot.is_active(): ;break if not right_parallel, adjust, cont.

    steps  = distance_fwd // MOVE_INCREMENTS
    offset = 0
    print(f"[move_right_parallel] -> Right aligning, dist {right_dist}")
    right_align()
    if right_dist:
        right_dist_current = dist_from_right_wall()
        print(f"[move_right_parallel] -> Current distance from wall: {right_dist_current}")

        ## Angle from current rotation to next rotation
        offset = math.degrees(math.atan( (right_dist - right_dist_current) / distance_fwd ))

        ## Calculate angle to get to next block center
    print(f"Move right parallel with offset {offset}")
    right_align( offset )
    for _ in range(steps):
        move( MOVE_INCREMENTS )
        ## Adjust a little extra to either side, to account for minor drifts
        right_align( offset - right_angle() / 2)
    move(distance_fwd % MOVE_INCREMENTS)





def dist_from_front_wall() -> float | None:
    """Returns blocks from center of robot to wall in front"""
    ## Assume front parallel
    return ( LATEST_ULTRASONICS['F'] ) + FRONT_FROM_CENTER

def front_back_align(row, col, orientation):
    """Calculate optimal angle based on front and back sensors compared to expected inputs.

    Orientation is number of 90 degree rotations clockwise from North.
    """
    targets = histogram.rotate_90(*histogram.distance_any_direction(row, col), times=-orientation)
    ## If values are significantly wrong, turn slightly in one direction, check if improved
    ## If improved, continue rotating until correct values appear, or until values worsen
    ## If not improved, change directions and do the same
    current  = scan_directions()
    print(current)
    print([histogram.limit_dist(c) for c in current])
    deltas   = [histogram.scale(c) - t for c, t in zip(current, targets)]
    rotate   = 5
    print(targets)
    print(deltas)
    ## Check that front and back values are as they should be
    for _ in range(ALIGN_RETRIES):
        if histogram.limit_dist(current[0]) == targets[0] and histogram.limit_dist(current[2]) == targets[2]:
            print("Done!")
            return
        robot.rotate(rotate)
        current = scan_directions()
        new_deltas = [histogram.scale(c) - t for c, t in zip(current, targets)]
        if (new_deltas[0] / deltas[0]) > ROTATE_ERR or (new_deltas[2] / deltas[2]) > ROTATE_ERR:
            rotate /= -2

        ## Calculated diff




def wall_align(steps_of_rotation: int = 5):
    ## TODO: Update using sensors on both sides - only need 180 degrees of rotation then
    ## TODO: Filter by angle threshold
    measured = []
    angles   = numpy.array([])
    for i in range(0, 360, steps_of_rotation):
        robot.rotate(steps_of_rotation)

        while( robot.is_active() ):
            time.sleep(0.01)
        time.sleep(0.1)

        ultrasonics = robot.ultrasonics()
        display.register_ultrasonic(ultrasonics)
        display.draw()
        measured = numpy.append(measured, [abs(wall_dist(ultrasonics))])
        angles = numpy.append(angles, [wall_angle(ultrasonics)])

    target = numpy.min(measured[numpy.where(numpy.absolute(angles) < 8)])

    # time.sleep(2)

    ERROR = 0.2
    print(numpy.where(measured == target))
    steps_back = len(measured) - numpy.where(measured == target)[0][0]
    rotate_back = -steps_of_rotation * steps_back
    # target = numpy.min(measured)
    # rotate_back = -steps_of_rotation * (len(measured) - numpy.argmin(measured))

    print(rotate_back)

    robot.rotate(rotate_back)

    while( robot.is_active() ):
        time.sleep( 0.01 )

    ## TODO: Calculate angle... adjust

    curr_angle = wall_angle(robot.ultrasonics())

    robot.rotate( - curr_angle / 2)

    while( robot.is_active() ):
        time.sleep( 0.01 )

    print(wall_angle(robot.ultrasonics()))

    print(measured)
    print(angles)


def scan_directions():
    ultrasonics = robot.ultrasonics()
    fwd = ultrasonics['F']
    right = (ultrasonics['FR'] + ultrasonics['BR']) / 2
    back  = ultrasonics['B']
    left  = (ultrasonics['FL'] + ultrasonics['BL']) / 2
    return fwd, right, back, left


def wall_angle(ultrasonics: dict):
    """Right-angle triangle, width is distance between sensors, height is difference in reading."""
    height = ultrasonics['FR'] - ultrasonics['BR']
    return math.degrees(math.atan( height / FR_BR ))


def wall_dist(ultrasonics: dict):
    return (ultrasonics['FR'] + ultrasonics['BR']) / 2

def wall_difference(ultrasonics: dict):
    return ultrasonics['FR'] - ultrasonics['BR']

def turns_to_opening(fwd, right, back, left):
    """Inputs are distances, returns number of 90 degree turns"""
    turns = numpy.argmax([fwd, right, back, left])
    if turns > 2:
        return 4 - turns
    return turns



############
### MAIN ###
############
# robot.led(0, 255, 0)

# display_thread.start()

_program_flow = """
1. Align with a wall (any wall).
2. Try to determine locations
3. Assuming a valid set of locations, move to next square, update locations
    -   Add some form of "history" tracking to prevent re-traversing old locations???
4. If actual location is determined, get position and determine distance to target

- Add handling of "edge" cases

"""
# wall_align()
# display.draw()

move_right_parallel(2, 6)
move_right_parallel(2, 6)
move_right_parallel(2, 6)
print("Done motion!")
raise Exception

right_align()
print(blocks_from_left_wall())
print(blocks_from_right_wall())

directions = scan_directions()

# print(directions)

res = histogram.determine_probabilities_unknown_direction(None, *directions)

# # Face towards greatest opening

# print(res)

for p in res:
    # print(p)
    histogram.draw(p)
    input("[ENTER] to continue...")

ultrasonics = get_ultrasonics()
display.register_ultrasonic(ultrasonics)
# if

# robot.rotate( 90 * turns_to_opening(*directions) )

# front_back_align(3, 0, 0)

# right_align()
# print(right_parallel())
# print(right_angle())

# move_right_parallel(12)

# while True:

#     ultrasonics = robot.ultrasonics()

#     print(wall_difference(ultrasonics))
#     # print(ultrasonics)
#     display.register_ultrasonic(ultrasonics)


#     display.draw()

#     time.sleep(1)


# left_align()

# right_align()

# print("Done")

# time.sleep(1)


# move_right_parallel(12)
