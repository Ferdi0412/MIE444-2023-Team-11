import time
import numpy
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
    return numpy.mean(readings)



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
        if (readings['FR'] - readings['BR']) < 0.5 and (readings['F'] > 12 or readings['B'] > 12 or ((readings['FL'] + readings['BL']) / 2) > 12):
            wall_align = True
        elif (readings['FL'] - readings['BL']) < 0.5 and (readings['F'] > 12 or readings['B'] > 12 or ((readings['FR'] + readings['BR']) / 2) > 12):
            wall_align = True
        elif diag_check:
            diag_align = True
        else:
            rotate(15)
            degrees_rotated += 15

    if diag_align:
        rotate(45)

def wall_align(increments: int = 36):
    """Align with wall. Do a 180 degree rotation (or at least attempt to)."""
    left_dist, left_alpha, right_dist, right_alpha = [], [], [], []

    for _ in range(increments):
        rotate( 180 // increments )
        # left_alpha.append(left_angle() if left_parallel() else numpy.nan)
        left_dist.append(dist_from_left_wall() or numpy.nan)
        # right_alpha.append(right_angle() if right_parallel() else numpy.nan)
        right_dist.append(dist_from_right_wall() or numpy.nan)

    left  = numpy.array(left_dist)
    right = numpy.array(right_dist)

    target_l = numpy.nanmin(left)
    target_r = numpy.nanmin(right)

    print(f"LEFT: {left}\nRIGHT: {right}\nL: {target_l}\nR: {target_r}")

    if target_l < target_r:
        print(f"Aiming for {target_l}")
        idx = numpy.where(left == target_l)[0][-1]
        left_aligned = True
    else:
        print(f"Aiming for {target_r}")
        idx = numpy.where(right == target_r)[0][-1]
        left_aligned = False

    print(f"Rotating {(increments - idx) * (180 // increments)} degrees")
    print(f"Increments: {increments}")
    print(f"IDX: {idx}")

    input("[ENTER] to align")

    for _ in range(increments - idx):
        rotate( - 180 // increments )

    return left_aligned






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

    wall_align()

    rotate_to_opening(scan_directions())

    if left_parallel():
        left_align()
    elif right_parallel():
        right_align()
    else:
        raise Exception("Unable to parallelize...")

    _localized = False
    probs = None

    while not _localized:
        probs = histogram.determine_probabilities_unknown_direction(probs, *scan_directions())

        if display_positions:
            for i, p in enumerate(probs):
                if histogram.is_valid_prob(p):
                    histogram.draw(p, title=histogram.DIRECTIONS[i])
                    input("[ENTER] to continue...")

############
### MAIN ###
############
wait_for_start()

# raise Exception("End of code...")

## TODO: Finish wall_align
nate_align()

input("[ENTER] to continue...")

rotate_to_opening(scan_directions())

if left_parallel():
    left_align()
elif right_parallel():
    right_align()
else:
    raise Exception

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
def align(located,selectSimmer):
    print('')
    print('Beginning Align')
    degreesRotated = -45
    diagAlign = False
    wallAlign = False
    rotateLeft(45, selectSimmer)
    while not diagAlign and not wallAlign:
        readings = sensorSweep(3,selectSimmer)
        #print(readings)

        diagCheck = True
        for i in readings:
            if i > 10:
                diagCheck = False
        closeCheck = readings[0] - readings[1]
        #print(closeCheck)
        if closeCheck < 0:
                closeCheck = -closeCheck
        #print(str(closeCheck))
        if closeCheck < 0.5 and readings[0] < 9.6 and (readings[2] > 12 or readings[3] > 12 or readings[4] > 12):
            wallAlign = True
        elif diagCheck:
            diagAlign = True
        else:
            rotateRight(15,selectSimmer)
            degreesRotated = degreesRotated + 15
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')

    if diagAlign:
        print('Diagonally Aligned')
    else:
        print('Wall Aligned')

    print('Degrees Rotated: '+str(degreesRotated))

    if located:
        if wallAlign:
            lockList = [0-degreesRotated, 90-degreesRotated, 180-degreesRotated, 270-degreesRotated, 360-degreesRotated]
            turnList = [0,-90,-180,-270,0]
        else:
            lockList = [-45-degreesRotated,45-degreesRotated, 135-degreesRotated, 225-degreesRotated, 315-degreesRotated, 405-degreesRotated]
            turnList = [45,-45,-135,-225,-315,-45]
        for k in range(len(lockList)):
            if lockList[k] < 0:
                lockList[k] = -lockList[k]
        #print(lockList)
        minLockListIndex = lockList.index(min(lockList))
        realignRotate = turnList[minLockListIndex]
        #print('r0-'+str(realignRotate))
        print('Rotating back: '+str(realignRotate))
        rotateRight(realignRotate, selectSimmer)
                #print('Rotation Complete')
            #else:
                #print('Still Rotating')

    else:
        if diagAlign:
            rotateLeft(45, selectSimmer)
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')

        readings = sensorSweep(1, selectSimmer)
        if readings[0] < 12:
            rotateRight(90, selectSimmer)
                    #print('Rotation Complete')
                #else:
                    #print('Still Rotating')

    return()
