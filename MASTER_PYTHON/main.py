import time
import numpy
import pandas
import math



from connector import Team_11_Robot
from connector._request import NoAcknowledge, NoReply
from maze import histogram, pathfind
import user_interface.display as display

#####################
### GLOBAL PARAMS ###
#####################
RETRIES = 5

FR_BR = 4 ## Distance from front right and back right sensors
FL_BL = 4 ## Distance from front left and back left sensors

RIGHT_FROM_CENTER = 2.6
LEFT_FROM_CENTER  = 2.6
FRONT_FROM_CENTER = 3.2
BACK_FROM_CENTER  = 3.2

ROBOT_MIN_ANGLE   = 180 / 40

## == MAIN ==
COM_PORT = "COM13"

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


##################
### ROBOT APIS ###
##################
def get_ultrasonics():
    global LATEST_ULTRASONICS
    readings = robot.ultrasonics()
    display.register_ultrasonic(readings)
    display.draw()
    LATEST_ULTRASONICS = readings
    return readings



def get_ultrasonics_multiple(count: int, delay: float = 0) -> dict:
    global LATEST_ULTRASONICS
    readings = robot.ultrasonic_json(count)
    display.register_ultrasonic_json(readings)
    display.draw()
    LATEST_ULTRASONICS = { sensor_id: sensor_mean(sensor_vals) for sensor_id, sensor_vals in readings.items() }
    return LATEST_ULTRASONICS



def sensor_mean(sensor_readings) -> float:
    readings = numpy.array(sensor_readings)
    readings = readings[numpy.where(readings > 0)]
    return numpy.mean(readings) if len(readings) > 0 else 0



def pass_time(sleep_s: int = 0.1):
    display.register_ultrasonic(robot.ultrasonics())
    time.sleep(sleep_s)



def rotate(angle: int):
    print("Call to robot.rotate(...)!")
    robot.rotate(angle)
    while robot.is_active():
        pass_time(0.05)



def move(distance_fwd: float):
    robot.move_forward(distance_fwd)
    while robot.is_active():
        pass_time(0.05)


def to_df(sensor_readings: dict[str, list[float]]) -> pandas.DataFrame:
    return pandas.DataFrame(list(sensor_readings.values()), columns=list(sensor_readings.keys()))


##################
### ALIGN LEFT ###
##################
def left_has_wall() -> bool:
    """Returns True if there is a wall detected close on the left side"""
    get_ultrasonics()
    return LATEST_ULTRASONICS['FL'] < 12 and LATEST_ULTRASONICS['BL'] < 12



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
    alpha = - (left_angle(3) - offset)
    for _ in range(ALIGN_RETRIES):
        if abs(alpha) <= ANGLE_THRESHOLD:
            return
        ## Adjustment should be reduced by half of alpha, in case of overshoot. Better to move several times
        adjustment = math.copysign(abs(alpha) - (ANGLE_THRESHOLD / 2), alpha)
        print(f"Making left-align adjustment of {adjustment} degrees.")
        rotate(adjustment)
        alpha = - (left_angle() - offset)




def left_parallel(offset: int = 0) -> bool:
    return (abs(left_angle() - offset) < ANGLE_THRESHOLD) and (LATEST_ULTRASONICS['FL'] > 0) and (LATEST_ULTRASONICS['BL'] > 0)



def move_left_parallel(distance_fwd, left_dist: int = None) -> None:
    """Move whilst trying to keep parallel to the right-side wall."""
    ## TODO: Figure out how to implement offset to re-center robot (if necessary).
    ## Solution for running without progress -> otherwise have a while robot.is_active(): ;break if not right_parallel, adjust, cont.

    steps  = distance_fwd // MOVE_INCREMENTS
    offset = 0
    print(f"[move_left_parallel] -> Right aligning, dist {left_dist}")
    left_align()
    if left_dist:
        left_dist_current = dist_from_left_wall()
        print(f"[move_right_parallel] -> Current distance from wall: {left_dist_current}")

        ## Angle from current rotation to next rotation
        offset = math.degrees(math.atan( (left_dist - left_dist_current) / distance_fwd ))

        ## Calculate angle to get to next block center
    print(f"Move right parallel with offset {offset}")
    left_align( offset )
    for _ in range(steps):
        move( MOVE_INCREMENTS )
        ## Adjust a little extra to either side, to account for minor drifts
        left_align( offset - left_angle() / 2)
    move(distance_fwd % MOVE_INCREMENTS)

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



###################
### ALIGN RIGHT ###
###################
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
    alpha = - (right_angle(3) - offset)
    for _ in range(ALIGN_RETRIES):
        if abs(alpha) <= ANGLE_THRESHOLD:
            return
        ## Adjustment should be reduced by half of alpha, in case of overshoot. Better to move several times.
        adjustment = math.copysign(abs(alpha) - (ANGLE_THRESHOLD / 2), alpha)
        print(f"Making right-align adjustment of {adjustment} degrees.")
        rotate(adjustment)
        alpha = - (right_angle() - offset)



def right_parallel(offset: int = 0) -> bool:
    return (abs(right_angle() - offset) <= ANGLE_THRESHOLD) and (LATEST_ULTRASONICS['FR'] > 0) and (LATEST_ULTRASONICS['BR'] > 0)



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




###################
### ALIGN FRONT ###
###################
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


def nate_align():
    print("Beginning [nate_align]")
    degrees_rotated = -45
    diag_align      = False
    wall_align      = False

    rotate(-45)

    while not diag_align and not wall_align:
        readings: dict = get_ultrasonics_multiple(3)

        diag_check = True
        for dist in readings.values():
            if dist > 10:
                diag_check = False
                break
        ## Update wall_align code here...
        if (readings['FR'] != 0 and readings['BR'] != 0) and (readings['FR'] - readings['BR']) < 0.5 and (readings['F'] > 12 or readings['B'] > 12 or ((readings['FL'] + readings['BL']) / 2) <= 12):
            print("Right wall appears aligned")
            if abs(abs(left_angle()) - 45) < ANGLE_THRESHOLD:
                diag_align = True
            else:
                rotate(-right_angle())
                wall_align = True
        elif (readings['FL'] != 0 and readings['BL'] != 0) and (readings['FL'] - readings['BL']) < 0.5 and (readings['F'] > 12 or readings['B'] > 12 or ((readings['FR'] + readings['BR']) / 2) <= 12):
            print("Left wall appears aligned")
            if abs(abs(right_angle()) - 45) < ANGLE_THRESHOLD:
                diag_align = True
            else:
                rotate(-left_angle())
                wall_align = True
        elif diag_check:
            print("Diagonally aligned!")
            diag_align = True
        else:
            print("Rotating another 15 degrees")
            rotate(15)
            degrees_rotated += 15

    if diag_align:
        print("Rotating 45 degrees")
        rotate(45)



def center_distance():
    """Returns adjustment to forward and right values for next block. From Nate's earlier 'center' function.
    Intention -> use to adjust movement to next block.
    """
    readings = pandas.Series(get_ultrasonics_multiple(10))
    readings %= 12
    readings[readings > 9.6] -= 12

    r_mean = (readings['FR'] + readings['BR']) / 2
    l_mean = (readings['FL'] + readings['BL']) / 2

    fb_diff = readings['F'] - readings['B']
    lr_diff = l_mean - r_mean

    if (fb_diff > 0 and readings['F'] < 3.5) or (fb_diff  < 0 and readings['B'] < 3.5):
        fb_diff = 0

    if (lr_diff > 0 and r_mean < 2.5) or (lr_diff < 0 and l_mean < 2.5):
        lr_diff = 0

    return fb_diff, lr_diff




def scan_directions():
    ultrasonics = robot.ultrasonics()
    fwd = ultrasonics['F']
    right = (ultrasonics['FR'] + ultrasonics['BR']) / 2
    back  = ultrasonics['B']
    left  = (ultrasonics['FL'] + ultrasonics['BL']) / 2
    return fwd, right, back, left



def rotate_to_opening(*directions):
    open_direction = numpy.argmax(numpy.array(directions) >= 12)
    rotate( 90 * open_direction )



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



def wait_for_start():
    while True:
        try:
            robot.led(0, 255, 0)
            return
        except (NoAcknowledge, NoReply):
            pass



def startup(display_positions = True):
    ## Try to localize:
    wait_for_start()

    nate_align()

    rotate_to_opening(scan_directions())

    nate_align()

    _localized = False
    probs      = None

    print("Starting localization")

    while not _localized:
        probs = histogram.determine_probabilities_unknown_direction(probs, *scan_directions())

        if display_positions:
            for i, p in enumerate(probs):
                if histogram.is_valid_prob(p):
                    histogram.draw(p, title=histogram.DIRECTIONS[i])
                    input("[ENTER] to continue...")

        break

############
### MAIN ###
############


wait_for_start()

nate_align()

print(turns_to_opening(*scan_directions()))

# rotate_to_opening(scan_directions())

# nate_align()

# fwd_offset, right_offset = center_distance()
# print(fwd_offset, right_offset)
# if fwd_offset != 0:
#     alpha = math.degrees(math.atan( right_offset / fwd_offset ))
#     rotate(-alpha)
#     move(fwd_offset)


# get_ultrasonics()
# def get_angle(height, base):
#     return math.degrees(math.atan(height / base))
# if abs(get_angle(LATEST_ULTRASONICS['FR'] - LATEST_ULTRASONICS['BR'], FR_BR) ) < 30:
#     right_align()

#print(to_df(get_ultrasonics_multiple(10)))


raise Exception("End of code...")

## TODO: Finish wall_align
startup()



probs = histogram.determine_probabilities_unknown_direction(None, *scan_directions())
for p in probs:
    # print(p)
    histogram.draw(p)
    input("[ENTER] to continue...")

ultrasonics = get_ultrasonics()
display.register_ultrasonic(ultrasonics)

if right_parallel():
    move_right_parallel(12)
# elif left_parallel():
#     move_left_parallel(12)
else:
    raise Exception("Could not find a parallel wall!")

probs = histogram.apply_movement_filter_unknown_direction(probs, 12, 0)

probs = histogram.determine_probabilities_unknown_direction(probs, *scan_directions())
for p in probs:
    # print(p)
    histogram.draw(p)
    input("[ENTER] to continue...")

# robot.move_forward(1)

# last_read = time.time()
# freq      = 0.1
# while True:
#     get_ultrasonics()
#     display.draw()
#     if time.time() > (last_read + freq):
#         print(f"Left side: {left_angle()}")
#         print(f"Right side: {right_angle()}d\n\n")
#         last_read = time.time()

raise Exception\

for _ in range(12):
    rotate(-90)
    time.sleep(1)

raise Exception

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
wall_align()
display.draw()

raise Exception

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


# # Face towards greatest opening

# print(res)

res = histogram.determine_probabilities_unknown_direction(None, *directions)
for p in res:
    # print(p)
    histogram.draw(p)
    input("[ENTER] to continue...")

ultrasonics = get_ultrasonics()
display.register_ultrasonic(ultrasonics)
# if

# robot.rotate( 90 * turns_to_opening(*directions) )

# front_back_align(3, 0, 0)


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


######################
### FROM NATE CODE ###
######################
def center(selectSimmer):
    print('')
    print('Beginning center')
    readings = to_df(get_ultrasonics_multiple(10))
    for i in range(len(readings)):
        while readings[i] > 12:
            readings[i] = readings[i] - 12

    for j in range(len(readings)):
        if readings[j] > 9.6:
            readings[j] = readings[j] - 12

    fbDifference = ((readings[0]+readings[1])/2) - readings[4]
    lrDifference = readings[2] - readings[3]

    #print(str(fbDifference) + ',' + str(lrDifference))
    if fbDifference > 0 and (readings[0] < 3.5 or readings[1] < 3.5):
        fbDifference = 0

    if fbDifference < 0 and readings[4] < 3.5:
        fbDifference = 0

    if lrDifference > 0 and readings[2] < 3.5:
        lrDifference = 0

    if lrDifference < 0 and readings[3] < 3.5:
        lrDifference = 0

    moveForward(fbDifference/2, selectSimmer)
    if selectSimmer:
        moveRight(lrDifference/2, selectSimmer)
