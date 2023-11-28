"""Strategies:

align_nate for when current block not known, or passing between two blocks without a block on right/left.

align_left/align_right for when current block is known and block to left or right for this and next block visited.

"""
######################
### BASE LIBRARIES ###
######################
import time, numpy, pandas, math, numbers



########################
### CUSTOM LIBRARIES ###
########################


## == Robot Control ==
from connector import Team_11_Robot
from connector._request import NoAcknowledge, NoReply

## == Localization and Navigation ==
from maze import histogram, pathfind

## == User Interface ==
import user_interface.display as display



#####################
### GLOBAL PARAMS ###
#####################
## == COLORS ==
class LedColours:
    one   = ['\x99', '\x88', '\xFE']
    two   = ['\x99', '\x50', '\xFE']
    three = ['\x55', '\x00', '\xCC']
    four  = ['\x00', '\x00', '\x56']

    startup     = [120, 120, 120]
    localized   = ['\x00', '\x33', '\x66']
    at_loading  = ['\x55', '\x00', '\xCC']
    found_block = ['\x99', '\x86', '\xFE']
    at_drop_off = ['\xAA', '\xFF', '\xFF']

    white       = ['\xAA', '\xFF', '\xFF']

## == MASTER ==
MANUAL_MODE        = False
LATEST_ULTRASONICS = {}
ANGLE_THRESHOLD    = 8
MOVE_INCREMENT     = 1
ALIGN_RETRIES      = 3
BLOCK_LEN          = 12



## == COMMUNICATION ==
COM_PORT       = "COM13"
SERIAL_RETRIES = 5



## == ROBOT-DIMENSIONS ==
FR_to_BR = 4
FL_to_BL = 4

CENTER_to_RIGHT = 2.6
CENTER_to_LEFT  = 2.6
CENTER_to_FRONT = 3.2
CENTER_to_BACK  = 3.2



## == LOCALIZATION ==
histogram.DISTANCE_THRESHOLD = 2



## == USER-INTERFACE ==
display.FPS      = 15
display.LIN_DIST = 10 # Distance on key-press 'w' or 's'
display.ROT_DIST = 15 # Distance on key-press 'q' or 'e'
def _go_manual(state: bool): global MANUAL_MODE; MANUAL_MODE = state
display.RobotController.go_manual = _go_manual



#############
### SETUP ###
#############
## == SERIAL ==
print("[Team_11_Robot] is getting set up")
robot = Team_11_Robot(COM_PORT, 2)

## == USER-INTERFACE ==
print("[display] is getting set up")
display.register_robot(robot)
display.init()
# display_thread = Thread(target = display.daemon, daemon=True)

## == LOCALIZATION ==
print("[histogram] is getting set up")
histogram.setup()


## == NAVIGATING ==
print("[pathfind] is getting set up")
pathfind.setup()


print("SETUP COMPLETE!", end='\n\n')



######################
### PHYSICAL ROBOT ###
######################
def get_ultrasonics():
    global LATEST_ULTRASONICS
    readings = robot.ultrasonics()
    display.register_ultrasonic(readings)
    display.draw()
    LATEST_ULTRASONICS = readings
    return readings



def _sensor_mean(sensor_readings) -> float:
    readings = numpy.array(sensor_readings)
    readings = readings[numpy.where(readings > 0)]
    return numpy.mean(readings) if len(readings) > 0 else 0



def get_ultrasonics_json(count: int, delay: float = 0) -> dict:
    global LATEST_ULTRASONICS
    readings = robot.ultrasonic_json(count)
    display.register_ultrasonic_json(readings)
    display.draw()
    LATEST_ULTRASONICS = { sensor_id: _sensor_mean(sensor_vals) for sensor_id, sensor_vals in readings.items() }
    return LATEST_ULTRASONICS



def pass_time(sleep_s: int = 0.1):
    display.register_ultrasonic(robot.ultrasonics())
    display.draw()
    time.sleep(sleep_s)



def rotate(angle: int):
    robot.rotate(angle)
    while robot.is_active():
        pass_time(0.05)



def move_forward(distance_fwd: float):
    robot.move_forward(distance_fwd)
    while robot.is_active():
        pass_time(0.05)



def stop():
    robot.stop()



def get_progress():
    return robot.progress()



def led(r, g, b):
    robot.led(r, g, b)



def blink_led(r, g, b, times: int, period: float = 0.5):
    for _ in range(times):
        robot.led(r, g, b)
        time.sleep(period / 2)
        robot.led_off()
        time.sleep(period / 2)


########################
### POSITION MEASURE ###
########################
def get_left_angle(avg_over: int = 1) -> float:
    """Clockwise angle from wall-parallel of the robot orientation."""
    measured = []
    for _ in range(avg_over or 1):
        ultrasonics = get_ultrasonics()
        measured.append(math.degrees(math.atan((ultrasonics['FL'] - ultrasonics['BL']) / FL_to_BL)))
    return numpy.mean(measured)



def check_left_parallel(offset: int = 0) -> bool:
    """Returns TRUE if within ANGLE_THRESHOLD."""
    return bool( (abs(get_left_angle() - offset) < ANGLE_THRESHOLD) and LATEST_ULTRASONICS['FL'] and LATEST_ULTRASONICS['BL'] )



def get_right_angle(avg_over: int = 1) -> float:
    """Clockwise angle from wall-parallel of the robot orientation."""
    measured = []
    for _ in range(avg_over or 1):
        ultrasonics = get_ultrasonics()
        measured.append(math.degrees(math.atan((ultrasonics['FR'] - ultrasonics['BR']) / FR_to_BR)))
    return numpy.mean(measured)



def check_right_parallel(offset: int = 0) -> bool:
    """Returns TRUE if within ANGLE_THRESHOLD."""
    return bool( (abs(get_right_angle() - offset) < ANGLE_THRESHOLD) and LATEST_ULTRASONICS['FR'] and LATEST_ULTRASONICS['BR'] )



def distance_from_left_wall() -> float | None:
    if not check_left_parallel():
        return None
    return ( LATEST_ULTRASONICS['FL'] + LATEST_ULTRASONICS['BL'] ) / 2 + CENTER_to_LEFT



def distance_from_right_wall() -> float | None:
    if not check_right_parallel():
        return None
    return ( LATEST_ULTRASONICS['FR'] + LATEST_ULTRASONICS['BR'] ) / 2 + CENTER_to_RIGHT



def get_directional_readings(number_of_readings: int = 1) -> tuple[float, float, float, float]:
    if number_of_readings:
        readings = get_ultrasonics_json(number_of_readings)
    else:
        readings = get_ultrasonics()
    fwd   = readings['F']
    left  = ( readings['FL'] + readings['BL'] ) / 2
    back  = readings['B']
    right = ( readings['FR'] + readings['BR'] ) / 2
    return fwd, right, back, left



def get_open_direction(number_of_readings: int = 1) -> int:
    """Returns number of clockwise 90 degree rotations to come to next open space."""
    readings = numpy.array(get_directional_readings())
    return numpy.where(readings > 12)[0][0]



###################
### ALIGN CODES ###
###################
def nate_align():
    print("Beginning [nate_align]")
    degrees_rotated = -45
    diag_align      = False
    wall_align      = False

    rotate(-45)

    while not diag_align and not wall_align:
        readings: dict = get_ultrasonics_json(3)

        diag_check = True
        for dist in readings.values():
            if dist > 10:
                diag_check = False
                break
        ## Update wall_align code here...
        if (readings['FR'] != 0 and readings['BR'] != 0) and (readings['FR'] - readings['BR']) < 0.5 and (readings['F'] > 12 or readings['B'] > 12 or ((readings['FL'] + readings['BL']) / 2) <= 12):
            print("Right wall appears aligned")
            if abs(abs(get_left_angle()) - 45) < ANGLE_THRESHOLD:
                diag_align = True
            else:
                rotate(-get_right_angle())
                wall_align = True
        elif (readings['FL'] != 0 and readings['BL'] != 0) and (readings['FL'] - readings['BL']) < 0.5 and (readings['F'] > 12 or readings['B'] > 12 or ((readings['FR'] + readings['BR']) / 2) <= 12):
            print("Left wall appears aligned")
            if abs(abs(get_right_angle()) - 45) < ANGLE_THRESHOLD:
                diag_align = True
            else:
                rotate(-get_left_angle())
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
        degrees_rotated += 45
    return degrees_rotated



def center_distance():
    """Returns adjustment to forward and right values for next block. From Nate's earlier 'center' function.
    Intention -> use to adjust movement to next block.
    """
    readings = pandas.Series(get_ultrasonics_json(10))
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



def _align_parallel(get_angle_function, offset: int = 0):
    """Calculate angle based off two right-side sensors."""
    alpha = - (get_right_angle(3) - offset)
    for _ in range(ALIGN_RETRIES):
        if abs(alpha) <= ANGLE_THRESHOLD:
            return
        ## Adjustment should be reduced by half of alpha, in case of overshoot. Better to move several times.
        adjustment = math.copysign(abs(alpha) - (ANGLE_THRESHOLD / 2), alpha)
        # print(f"Making right-align adjustment of {adjustment} degrees.")
        rotate(adjustment)
        alpha = - (get_angle_function() - offset)



def align_left_parallel(offset: int = 0):
    _align_parallel(check_left_parallel, offset)



def align_right_parallel(offset: int = 0):
    _align_parallel(check_right_parallel, offset)



###################################################
### MOVEMENTS FUNCTIONS FOR SIDE-WALL ALIGNMENT ###
###################################################
def _move_side_parallel(align_function, fwd_distance: float, angle_offset: int = 0):
    align_function( angle_offset )
    for _ in range( fwd_distance // MOVE_INCREMENT ):
        move_forward( MOVE_INCREMENT )
        align_function( angle_offset )



def move_left_parallel(fwd_distance: float, angle_offset: int = 0):
    _move_side_parallel(align_left_parallel, fwd_distance, angle_offset)



def move_right_parallel(fwd_distance: float, angle_offset: int = 0):
    _move_side_parallel(align_right_parallel, fwd_distance, angle_offset)



def _move_to_next_center(align_function, side_distance_function, fwd_distance: float, side_distance_target: float = 6):
    distance_moved = 0
    get_offset = lambda: math.degrees( math.atan( ( side_distance_target - side_distance_function() ) / ( fwd_distance - distance_moved ) ) )
    align_function(get_offset())
    for _ in range( fwd_distance // MOVE_INCREMENT ):
        move_forward( MOVE_INCREMENT )
        distance_moved += MOVE_INCREMENT
        align_function( get_offset() )



def move_to_next_center_left(fwd_distance, side_distance = 6):
    _move_to_next_center(align_left_parallel, fwd_distance, side_distance)



def move_to_next_center_right(fwd_distant, side_distance = 6):
    _move_to_next_center(align_right_parallel, fwd_distant, side_distance)



##################################
### CODES TO DEFINE BEHAVIOURS ###
##################################
TARGET_POSITIONS    = [(0, 2), (2, 0)]

CURRENT_POSITION    = None
CURRENT_ORIENTATION = None
PROBABILITIES       = None


def take_x_r_inputs():
    try:
        x = int(input("\n\n[ENTER] Number of blocks moved forward (-ve for negative):\n"))
    except ValueError:
        print("An error in taking inputs occured...")
        return None, None# take_x_r_inputes()
    try:
        r = int(input("\n\n[ENTER] Number of 90 degree rotations clockwise (key_'e' direction; -ve for counter-clockwise):\n"))
    except ValueError:
        print("An error in taking inputs occured...")
        return None, None# take_x_r_inputes()
    print("Done taking inputs...")
    return x, r



def localize_global() -> None:
    global PROBABILITIES, CURRENT_ORIENTATION, CURRENT_POSITION

    ## Get user inputs
    movements_fwd, rotations_clockwise = take_x_r_inputs()

    ## Check inputs are valid
    if movements_fwd is None or rotations_clockwise is None:
        return ## Do nothing if invalid inputs

    ## Check if PROBABILITIES has yet been generated.
    if PROBABILITIES is not None:
        PROBABILITIES = histogram.apply_movement_filter_unknown_direction(PROBABILITIES, movements_fwd, 0, rotations_clockwise)

    ## Generate probabilities given position
    PROBABILITIES = histogram.determine_probabilities_unknown_direction(PROBABILITIES, *get_directional_readings(10))

    ## Display plots
    histogram.draw_set(PROBABILITIES)
    histogram.draw_clear()

    ## See if a single valid direction has been found...
    if histogram.determine_direction(PROBABILITIES):
        print("\n\n!!!HURRAY!!!\n\nYOU HAVE LOCALIZED.")
        CURRENT_ORIENTATION = histogram.determine_direction(PROBABILITIES)
        CURRENT_POSITION = histogram.get_locations(PROBABILITIES[CURRENT_ORIENTATION])



def localize_oneoff() -> None:
    ## Display "one-off" localization
    histogram.draw_set(histogram.determine_probabilities_unknown_direction(None, *get_directional_readings(10)))
    histogram.draw_clear()



display.RobotController.localize_global = localize_global
display.RobotController.localize_oneoff = localize_oneoff



def path_to_loading_zone():
    if CURRENT_POSITION is not None:
        print("Displaying path to LOADING ZONE")
        path_1 = pathfind.get_shortest_path(CURRENT_POSITION, (1, 3))
        path_2 = pathfind.get_shortest_path(CURRENT_POSITION, (3, 1))
        pathfind.draw(path_1 if (len(path_1) <= len(path_2)) else path_2)
        input("[ENTER] to continue...")
    else:
        print("Not yet localized...")



def take_x_y_inputs(prefix: str = ''):
    try:
        y = int(input(f"\n\n[ENTER] {prefix} ROW:\n"))
    except ValueError:
        print("An error in taking inputs occured...")
        return None, None# take_x_r_inputes()
    try:
        x = int(input(f"\n\n[ENTER] {prefix} COL:\n"))
    except ValueError:
        print("An error in taking inputs occured...")
        return None, None# take_x_r_inputes()
    print("Done taking inputs...")
    return y, x



def path_to_location():
    if CURRENT_POSITION is None:
        print("Not yet localized...")
        return
    row, col = take_x_y_inputs()
    if row is not None and col is not None:
        print(f"Displaying shjortet path to ({row}, {col})")
        path = pathfind.get_shortest_path(CURRENT_POSITION, (row, col))
        pathfind.draw(path)
        input("[ENTER] to continue...")
        pathfind.close_plt()




def manual_path():
    curr_row, curr_col = take_x_y_inputs("current")

    if curr_row is None or curr_col is None:
        print("INVALID...")
        return

    to_row, to_col = take_x_y_inputs("target")

    if to_row is None or to_col is None:
        print("INVALID...")
        return

    path = pathfind.get_shortest_path((curr_row, curr_col), (to_row, to_col))
    pathfind.draw(path)
    input("[ENTER] to continue...")
    pathfind.close_plt()


display.RobotController.manual_path          = manual_path
display.RobotController.path_to_loading_zone = path_to_loading_zone
display.RobotController.path_to_location     = path_to_location


def wait_for_comms():
    while True:
        try:
            robot.led(0, 255, 0)
            return
        except (NoAcknowledge, NoReply):
            pass



def setup_position():
    """Center and wall-align robot (as appropriate)."""
    ## Align with walls
    nate_align()

    print("First nate_align done!")

    dist_fwd, dist_right = center_distance()

    while dist_fwd == 0:
        move_forward(0.1)
        dist_fwd, dist_right = center_distance()

    alpha = math.degrees( math.atan( dist_right / dist_fwd ) )

    rotate(-alpha - ANGLE_THRESHOLD / 2)

    print(f"Distances from center of block: {(dist_fwd, dist_right)}")
    move_forward( - dist_fwd )

    ## TODO:
    ## - Add some way to handle centering

    ## Move to nearest wall in front or behind it - aim for within 3 inches, as this means robot is in center of square
    while True:
        readings = get_ultrasonics_json(5)

        if readings['F'] < readings['B'] and readings['F'] != 0:
            print("First case...")
            move_forward(readings['F'] - 3)

        elif readings['B'] != 0:
            print("Second case...")
            move_forward( - readings['B'] + 3)

        elif readings['F'] != 0:
            print("Third case...")
            move_forward( readings['F'] - 3 )

        else:
            print("Re-aligning...")
            nate_align()
            continue

        break



def localize(position_setup: bool = False):
    print("\n\nStarting localize...")

    global CURRENT_POSITION, CURRENT_ORIENTATION, PROBABILITIES
    localized = False
    if not position_setup:
        setup_position()

    probs = histogram.determine_probabilities_unknown_direction(None, *get_directional_readings())

    while not localized:
        ## Check MANUAL_MODE flag at least once per loop
        if MANUAL_MODE:
            display.draw()
            continue

        histogram.draw_set(probs)

        if isinstance( histogram.determine_direction(probs), numbers.Number ):
            orientation = histogram.determine_direction(probs)
            print(f"Successfully localized!")
            print(f"Currently in orientation {histogram.DIRECTIONS[orientation]}")
            print(f"Currently at location {histogram.get_locations(probs[orientation])}")
            localized = True
            PROBABILITIES       = probs[orientation]
            CURRENT_ORIENTATION = orientation
            CURRENT_POSITION    = histogram.get_locations(probs[orientation])
            blink_led(*LedColours.localized, 5)
            input("Press [ENTER] to continue!")
            return

        ## Calculate how many rotations need to be made to get to next open space
        rotations_to_make = get_open_direction(5)
        print(f"Rotating {rotations_to_make * 90} degrees...")

        ## Update probs to represent this rotation
        probs = histogram.rotate_90(*probs, rotations_to_make)
        ## Rotate robot to match this
        rotate( rotations_to_make * 90 )

        print(f"Moving forward 12 inches...")
        for _ in range( 4 ):
            if check_right_parallel():
                print("LEFT aligned...")
                align_left_parallel()
                move_right_parallel( 3 )

            elif check_left_parallel():
                print("RIGHT aligned...")
                align_right_parallel()
                move_left_parallel( 3 )

            else:
                print("NO alignment")
                ## Pray it moves forwards
                # nate_align()
                move_forward( 3 )
            # nate_align()
            # move_forward(3)

        probs = histogram.apply_movement_filter_unknown_direction(probs, 12, 0)
        probs = histogram.determine_probabilities_unknown_direction(probs, *get_directional_readings())





def navigate_to_neighbouring_block(to_row, to_col):
    global CURRENT_POSITION, CURRENT_ORIENTATION, PROBABILITIES
    curr_row, curr_col = CURRENT_POSITION

    left_align, right_align = False, False

    ## Calculate how to get to next block
    if curr_row > to_row:
        target_orientation = histogram.DIRECTIONS.SOUTH
        left_align         = histogram.WALLS[to_row, curr_col+1]
        right_align        = histogram.WALLS[to_row, curr_col-1]

    elif curr_row < to_row:
        target_orientation = histogram.DIRECTIONS.NORTH
        left_align         = histogram.WALLS[to_row, curr_col-1]
        right_align        = histogram.WALLS[to_row, curr_col+1]

    elif curr_col > to_col:
        target_orientation = histogram.DIRECTIONS.WEST
        left_align         = histogram.WALLS[to_row+1, curr_col]
        right_align        = histogram.WALLS[to_row-1, curr_col]

    elif curr_col < to_col:
        target_orientation = histogram.DIRECTIONS.EAST
        left_align         = histogram.WALLS[to_row-1, curr_col]
        right_align        = histogram.WALLS[to_row+1, curr_col]

    else:
        raise ValueError ("No change to reach next block!")

    ## If rotation required, rotate then re-align
    rotation_required = target_orientation - CURRENT_ORIENTATION
    if ( rotation_required ) > 0:
        rotate(rotation_required)
        if left_align and get_left_angle() < 20:
            align_left_parallel()
        elif right_align and get_right_angle() < 20:
            align_right_parallel()
        else:
            nate_align()

    ## If walls available on either side, follow these
    if left_align:
        move_left_parallel( BLOCK_LEN )
    elif right_align:
        move_right_parallel( BLOCK_LEN )
    else:
        move_forward( BLOCK_LEN )

    ## Update to represent new position and orientation
    CURRENT_POSITION    = (to_row, to_col)
    CURRENT_ORIENTATION = target_orientation

    ## Update probabilities table/matrix
    p = PROBABILITIES
    p = histogram.apply_movement_filter(to_row - curr_row, to_col - curr_col)
    p = histogram.determine_probabilities(p, histogram.rotate_90(*get_directional_readings(), target_orientation))
    PROBABILITIES       = p

    blink_led(*LedColours.white, 2)
    time.sleep(0.2)
    # ~ navigate_to_neighbouring_block(...)



def navigate_to_loading_zone():
    path_options = [pathfind.get_shortest_path(CURRENT_POSITION, p) for p in TARGET_POSITIONS]
    path_lens    = [len(option) for option in path_options]
    selection    = path_options(numpy.argmin(path_lens)[0][0])

    for target_block in selection:
        navigate_to_neighbouring_block(*target_block)
    blink_led(*LedColours.at_loading, 5)


def search_for_block():
    pass



def pickup_block():
    pass



def go_to_dropoff(target_position):
    ## TODO: Add checks for block being in position using ultrasonic "G"
    path = pathfind.get_shortest_path(target_position, CURRENT_POSITION)

    for target_block in path:
        navigate_to_neighbouring_block(*target_block)
    blink_led(*LedColours.at_drop_off)



def drop_block():
    pass



############
### MAIN ###
############

if __name__ == '__main__':
    wait_for_comms()

    # blink_led(*LedColours.startup, 5)

    while True:
        display.draw()
        get_ultrasonics()

    # setup_position()

    # localize( True )

    # exit()

    # navigate_to_loading_zone()
