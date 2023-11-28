######################
### BASE FUNCTIONS ###
######################
import numpy  as _numpy
import pandas as _pandas



############
### DEFS ###
############
MAZE = _numpy.array([['C', 'T', 'H', 'C', 'E', 'D', 'E', 'D'],
                     ['T', 'C', 'E', 'C', 'H', 'F', 'H', 'T'],
                     ['H', 'E', 'D', 'E', 'E', 'H', 'E', 'H'],
                     ['C', 'H', 'T', 'H', 'H', 'C', 'E', 'D'],])

OPEN_READING = 7

NORTH = 1
SOUTH = 2
EAST  = 3
WEST  = 4


############
### MAIN ###
############
# def filter_prediction_array(earlier_predictions: tuple[_numpy.array, _numpy.array], max_vals, down, right):
#     vals = (earlier_predictions[0] + down, earlier_predictions[1] + right)
#     print((earlier_predictions[1] < 0))
#     to_keep = _numpy.where(~(earlier_predictions[0] >= max_vals[0]) + (earlier_predictions[0] < 0)\
#                              + (earlier_predictions[1] >= max_vals[1]) + (earlier_predictions[1] < 0))
#     return (vals[0][to_keep], vals[1][to_keep])



############
### MAZE ###
############
# maze_up    = filter_prediction_array(MAZE, MAZE.shape, -1, 0)
# maze_down  = filter_prediction_array(MAZE, MAZE.shape, 1, 0)
# maze_left  = filter_prediction_array(MAZE, MAZE.shape, 0, -1)
# maze_right = filter_prediction_array(MAZE, MAZE.shape, 0, 1)



############
### MAIN ###
############
def predict_room_type(sensor_readings: _numpy.array):
    """Determine what location you may be at b on sensor_readings.

    NOTE: Assumes that robot is appropriately aligned.
    """
    directional_readings = _numpy.array([sensor_readings[0:2].mean(), *sensor_readings[2:5]])
    open_directions      = directional_readings >= OPEN_READING
    walls_found          = open_directions.astype(int).sum()

    ## Walls on 3 sides
    if 3 == walls_found:
        return 'D'

    ## Walls on 2 opposite sides - HALL
    elif 2 == walls_found and (open_directions[0] == open_directions[3]):
        return 'H'

    ## Walls on 2 joined sides - Corner
    elif 2 == walls_found:
        return 'C'

    ## Walls on 1 side
    elif 1 == walls_found:
        return 'T'

    ## Walls on no sides
    else:
        return 'F'




def predict_first_location(sensor_readings: _numpy.array):
    """Predict location base on wall readings."""
    # print(sensor_readings)
    locations  = _numpy.where(MAZE == predict_room_type(sensor_readings))
    # directions = _numpy.array([_numpy.nan] * len(sensor_readings))
    print("Potential locations [No estimates on direction yet....]:")
    for row, col in zip(*locations):
        print(f"Row: {row}\tColumns: {col}")
    # directions = _numpy.array([_numpy.nan] * len(locations))
    return locations



def predict_location(earlier_predictions: tuple[_numpy.array, _numpy.array], sensor_readings: _numpy.array):
    """Predict location based on wall readings.
    Works on being in a neighbouring block.
    TODO: Add a '# blocks moved'.
    """
    pass
    # if earlier_predictions is None:
    #     return predict_first_location(sensor_readings)

    # room_type = predict_room_type(sensor_readings)

    # move_down_matches    = filter_prediction_array(_numpy.where(maze_down  == room_type), ())
    # move_up_matches      = _numpy.where(maze_up    == room_type)
    # move_right_matches   = _numpy.where(maze_right == room_type)
    # move_left_matches    = _numpy.where(maze_left  == room_type)



    # move_up_matches    = _numpy.intersect1d(MAZE[ :-1, : ], earlier_predictions, return_indices=True)
    # move_down_matches  = _numpy.intersect1d(MAZE[ 1: , : ], earlier_predictions)
    # move_right_matches = _numpy.intersect1d(MAZE[ :, :-1 ], earlier_predictions)
    # move_left_matches  = _numpy.intersect1d(MAZE[ :,  1: ], earlier_predictions)



