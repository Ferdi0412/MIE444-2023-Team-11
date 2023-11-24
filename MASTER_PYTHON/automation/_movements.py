import numpy as _numpy
import time  as _time

import sys, os; print(os.path.dirname(os.path.dirname(__file__))); sys.path.append(os.path.dirname(os.path.dirname(__file__))); from MASTER_PYTHON.connector.sender import Team_11_Robot as Team_11_Client; _=sys.path.pop()


DIST_FILTER        = 72
EMERGENCY_DIST     = 2.5
DIAG_THRESHOLD     = 10
PARALLEL_THRESHOLD = 1
CLOSE_THRESHOLD    = 9.6
FAR_THRESHOLD      = 12
BLOCK_LEN          = 12
DIFF_THRESHOLD     = 3.5

LOCK_LIST = [0, 90, 180, 270, 360, 450]
TURN_LIST = [0, -90, -180, -270, -360]

def _sensor_mean(sensor_readings):
    readings = _numpy.array(sensor_readings)
    ## Filter by UPPER and LOWER thresholds
    readings = readings[readings >= 0]
    readings = readings[readings < DIST_FILTER]
    return readings.mean()

def sensor_sweep(robot, number_sweeps):
    sensor_data = robot.ultrasonic_json(number_sweeps)
    return _numpy.array([_sensor_mean(readings) for readings in sensor_data.values()])

def emergency_check(sensor_data: _numpy.array):
    return any(sensor_data < EMERGENCY_DIST), (sensor_data < EMERGENCY_DIST)

def emergency_move_sideways(robot, right):
    angle = 90 if right else -90
    robot.rotate(angle)
    while robot.is_active():
        _time.sleep(0.1)
    robot.move_forward(1)
    while robot.is_active():
        _time.sleep(0.1)
    robot.rotate(-angle)
    while robot.is_active():
        _time.sleep(0.1)

def emergency_move(robot, emergency_check_results):
    emergency_count = emergency_check_results.sum()
    if (emergency_count == 2) and (emergency_check_results[0] or emergency_check_results[1]):
        robot.move_forward(-1)
    elif (emergency_count == 1) and emergency_check_results[2]:
        emergency_move_sideways(robot, True)
    elif (emergency_count == 1) and emergency_check_results[3]:
        robot.move_forward(-1)
    elif (emergency_count == 1) and emergency_check_results[4]:
        emergency_move_sideways(robot, False)
    else:
        raise Exception("Several directions with emergency triggers!")
    while robot.is_active():
        _time.sleep(0.1)

def move_forward(robot, distance):
    robot.move_forward(distance)
    while robot.is_active():
        _time.sleep(0.1)
        sensor_readings = sensor_sweep(robot, 5)
        alarm, alarm_list = emergency_check(sensor_readings)
        if alarm:
            robot.stop()
            progress = robot.progress()
            emergency_move(robot, alarm_list)
            robot.move_forward(distance * (1 - progress))

def rotate_right(robot, angle):
    robot.rotate(angle)
    while robot.is_active():
        _time.sleep(0.1)

def rotate_left(robot, angle):
    robot.rotate(-angle)
    while robot.is_active():
        _time.sleep(0.1)

def move_right(robot, distance):
    rotate_right(robot, 90)
    move_forward(robot, distance)
    rotate_left(robot, 90)

def align(robot, is_localized):
    diagonally_aligned, wall_aligned = False, False
    degrees_rotated = -45
    rotate_left(robot, 45)
    while not (diagonally_aligned and wall_aligned):
        sensor_readings = sensor_sweep(robot, 3)

        diagonal_check = any(sensor_readings > DIAG_THRESHOLD)

        front_parallel = abs(sensor_readings[0] - sensor_readings[1])

        if (front_parallel < PARALLEL_THRESHOLD) and (sensor_readings[0] < CLOSE_THRESHOLD) and (any(sensor_readings[2:] > FAR_THRESHOLD)):
            wall_aligned = True
        elif diagonal_check:
            diagonally_aligned = True
        else:
            rotate_right(robot, 3)
            degrees_rotated += 3

    if is_localized:
        if wall_aligned:
            lock_list = _numpy.absolute(_numpy.array(LOCK_LIST)[:-1] - degrees_rotated)
            turn_list = _numpy.array(TURN_LIST) % 360
        else:
            lock_list = _numpy.absolute(_numpy.array(LOCK_LIST) - 45 - degrees_rotated)
            turn_list = (_numpy.array(TURN_LIST) + 45) % 360
        min_lock_index = lock_list.argmin()
        realign_rotate = turn_list[min_lock_index]
        rotate_right(robot, realign_rotate)

    else:
        if diagonally_aligned:
            rotate_left(45, robot)

        readings = sensor_sweep(robot, 1)

        if readings[0] < BLOCK_LEN:
            rotate_right(robot, 90)

def center(robot):
    sensor_readings = sensor_sweep(robot, 10)
    sensor_readings[sensor_readings > BLOCK_LEN] -= BLOCK_LEN
    sensor_readings[sensor_readings > CLOSE_THRESHOLD] -= BLOCK_LEN

    front_back_diff = sensor_readings[0:2].mean() - sensor_readings[3]

    left_right_diff = sensor_readings[2] - sensor_readings[3]

    if front_back_diff > 0 and ( any(sensor_readings[0:2] < DIFF_THRESHOLD)):
        front_back_diff = 0

    if front_back_diff < 0 and sensor_readings[3] < DIFF_THRESHOLD:
        front_back_diff = 0

    if left_right_diff > 0 and sensor_readings[2] < DIFF_THRESHOLD:
        left_right_diff = 0

    if left_right_diff < 0 and sensor_readings[4] < DIFF_THRESHOLD:
        left_right_diff = 0

    move_forward(robot, front_back_diff)
    move_right(robot, left_right_diff)

def room_detector(robot):
    sensor_readings = sensor_sweep(robot, 10)

    directional_readings = _numpy.array([sensor_readings[0:2].mean(), *sensor_readings[2:5]])

    room_sequence = directional_readings > BLOCK_LEN

    number_of_walls = room_sequence.astype(int).sum()

    if number_of_walls == 3:
        room_type = 'D'
    elif number_of_walls == 2 and room_sequence[0] == True:
        room_type = 'H'
    elif number_of_walls == 2:
        room_type = 'C'
    elif number_of_walls == 1:
        room_type = 'T'
    else:
        room_type = 'F'
    print(f"[room_detector] -> Room type: {room_type}")
    return sensor_readings, room_type

def find_new_locations_first(robot, location_list)

def find_new_locations(robot, location_list, maze, room_type, step_one):
