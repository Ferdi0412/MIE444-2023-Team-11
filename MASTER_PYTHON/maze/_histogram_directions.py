"""Histogram, but everything uses sets to check positions.

There are 2 combinations of readings that have more than 1 occurance, these two occur in a total of 5 locations.
"""


## TODO ##
## READ: https://numpy.org/doc/stable/user/basics.rec.html
## More logical indexing...
## Using "Structured arrays"


######################
### BASE LIBRARIES ###
######################
import numpy as _np
import sys, os
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

########################
### CUSTOM LIBRARIES ###
########################
sys.path.append(os.path.dirname(__file__))

from _maze import OPEN

_=sys.path.pop()

#################
### CONSTANTS ###
#################
WALLS = _np.pad( ((OPEN - 1) * -1), 1, 'constant', constant_values=1 )
MAZE  = None

KERNEL = _np.array([[0.1, 0.1, 0.1],
                    [0.1, 0.8, 0.1],
                    [0.1, 0.1, 0.1]])

# KERNEL = _np.array([[0.0, 0.0, 0.0],
#                     [0.0, 0.8, 0.0],
#                     [0.0, 0.0, 0.0]])

P_HIT  = 0.6
P_MISS = 0.2

RESOLUTION = 12

DISTANCE_THRESHOLD = 3

POS_T = _np.dtype([('row', '<i4'), ('col', '<i4')])

REPEATED      = None
REPEAT_COUNTS = None

_INVALID_DIRECTION = object()

class DIRECTIONS (object):
    NORTH = 0
    EAST  = 1
    SOUTH = 2
    WEST  = 3

    def __class_getitem__(cls, val) -> str:
        print(val)
        """Return string representation of direction."""
        return ['NORTH', 'EAST', 'SOUTH', 'WEST'][val]

#########################
### PRIVATE FUNCTIONS ###
#########################
def _generate_maze(resolution):
    """Initialize MAZE."""
    maze = _np.array( [[_np.nan] * OPEN.shape[1]] * OPEN.shape[0],
                      dtype = _np.dtype( [('NORTH', '<f4'),
                                          ('EAST',  '<f4'),
                                          ('SOUTH', '<f4'),
                                          ('WEST',  '<f4')] ) )
    for row in range( 1, maze.shape[0] + 1 ):
        for col in range( 1, maze.shape[1] + 1):
            if WALLS[row, col]:
                maze[row-1, col-1] = tuple([-1, -1, -1, -1,])
                continue

            east  = min( _np.argmax( WALLS[row, col-1 :: -1] ), DISTANCE_THRESHOLD )
            west  = min( _np.argmax( WALLS[row, col+1 :    ] ), DISTANCE_THRESHOLD )
            north = min( _np.argmax( WALLS[row-1 :: -1, col] ), DISTANCE_THRESHOLD )
            south = min( _np.argmax( WALLS[row+1 :,     col] ), DISTANCE_THRESHOLD )

            maze[row-1, col-1] = tuple([north, east, south, west,])
    return _np.repeat( _np.repeat( maze, resolution, axis=1 ), resolution, axis=0 )



def _non_unique_counts(some_array: _np.array) -> list[int]:
    _, occ_counts = _np.unique(some_array, return_counts=True)
    return occ_counts[_np.where(occ_counts > (RESOLUTION ** 2))] // (RESOLUTION ** 2)



def _non_unique(some_array: _np.array) -> _np.array:
    """Return the indices of all non-unique measurements."""
    occ_vals, occ_counts = _np.unique(some_array, return_counts=True)
    return occ_vals[_np.where(occ_counts > (RESOLUTION ** 2))]



def _search_for_tuple(search_array: _np.array, search_target: tuple) -> _np.array:
    """Returns 'search_array == search_target' when the elements in search_array are tuples."""
    return search_array == _np.array([search_target], dtype = search_array.dtype)



def _print_maze():
    print(MAZE[::RESOLUTION, ::RESOLUTION])



########################
### PUBLIC FUNCTIONS ###
########################
def setup():
    global MAZE, REPEATED, REPEAT_COUNTS
    MAZE          = _generate_maze(RESOLUTION)
    REPEATED      = _non_unique(MAZE)[1:] ## Drop the WALL value
    REPEAT_COUNTS = _non_unique_counts(MAZE)[1:]  ## Drop the WALL counts



def rotate_90(north, east, south, west, times: int = 1) -> tuple:
    """Returns input item of {north} {east} {south} and {west} rotated by 90 degrees clockwise.

    ie. rotate_90(1, 2, 3, 4, 2) -> returns (3, 4, 1, 2)
    """
    ## If times > 0 -> Rotate 90 degrees clockwise
    ## Global north is now on your side that was earlier west
    if times > 0:
        for _ in range(times):
            temp  = north
            north = east
            east  = south
            south = west
            west  = temp
    ## If times < 0 -> Rotate 90 degrees counter-clockwise
    ## Global north is now on your side that was earlier east
    else:
        for _ in range(-times):
            temp  = north
            north = west
            west  = south
            south = east
            east  = temp
    ## Return the new stuff!
    return north, east, south, west



def rotate_90_prob_sets(prob_sets, times: int = 1) -> tuple:
    """Returns prob_sets rotated by 90 degrees."""
    return rotate_90(*prob_sets, times)



def draw(probabilities: _np.array) -> None:
    """Display a probabilities plot."""
    plt.close()
    plt.matshow(probabilities)
    plt.draw()
    plt.pause(0.001)



#######################################
### FUNCTIONS GIVEN KNOWN DIRECTION ###
#######################################
def get_locations(probabilities: _np.array) -> list[tuple[float, float]]:
    """Get list of (row, col) the robot may currently be in given a probabilities set."""
    pos_tuple = _np.where(probabilities == probabilities.max())
    return _np.unique( _np.array( list(zip(pos_tuple[0] // RESOLUTION, pos_tuple[1] // RESOLUTION)), dtype=POS_T ).T ) #pos_x_y[0] // RESOLUTION, pos_x_y[1] // RESOLUTION



def determine_probabilities(probabilities: _np.array, north_blocks, east_blocks, south_blocks, west_blocks):
    """If facing NORTH, right becomes EAST."""
    if probabilities is None:
        probabilities = _np.ones( MAZE.shape )

    p_update = _np.ones( MAZE.shape, _np.float64 ) * P_MISS

    p_update[ _search_for_tuple( MAZE, tuple([min(north_blocks, DISTANCE_THRESHOLD),
                                              min(east_blocks,  DISTANCE_THRESHOLD),
                                              min(south_blocks, DISTANCE_THRESHOLD),
                                              min(west_blocks,  DISTANCE_THRESHOLD)]) ) ] = P_HIT

    #p_update[ MAZE == 0 ] = 0

    probabilities = _np.multiply(p_update, probabilities)

    probabilities /= _np.sum(probabilities)

    return probabilities



def apply_movement_filter(x_steps: int, y_steps: int, probabilities: _np.array, *, ignore_kernel: bool = False):
    """Convolution on probabilities to account for movement errors. MOVE step of histogram.

    x_steps and y_steps are in inches north and east respectively.
    """
    ## Move rightwards/leftwards (across columns)
    if x_steps > 0:
        probabilities[:, x_steps:] = probabilities[:, :-x_steps]
        probabilities[:, :x_steps] = 0

    elif x_steps < 0:
        probabilities[:, :x_steps] = probabilities[:, (-x_steps):]
        probabilities[:, x_steps:] = 0

    ## Move upwards/downwards (across rows)
    if y_steps > 0:
        probabilities[y_steps:, :] = probabilities[:-y_steps, :]
        probabilities[:y_steps, :] = 0

    elif y_steps < 0:
        probabilities[:y_steps, :] = probabilities[(-y_steps):, :]
        probabilities[y_steps:, :] = 0

    if not ignore_kernel:
        probabilities = convolve2d(probabilities, KERNEL, 'same')

    probabilities[ _search_for_tuple( MAZE, tuple([-1, -1, -1, -1]) ) ] = 0

    return probabilities



#######################################
### FUNCTIONS FOR UNKNOWN DIRECTION ###
#######################################
def _determine_probabilities(probabilities: _np.array, north_blocks, east_blocks, south_blocks, west_blocks) -> _np.ndarray:
    """Runs determine_probabilities only if input is not _INVALID_DIRECTION"""
    if probabilities is not _INVALID_DIRECTION:
        probabilities = determine_probabilities(probabilities, north_blocks, east_blocks, south_blocks, west_blocks)
    return probabilities



def _valid_probs_check(probabilities: _np.array) -> _np.array:
    if probabilities is _INVALID_DIRECTION:
        return _INVALID_DIRECTION
    count_of_potential_positions = len(get_locations(probabilities))
    if count_of_potential_positions == 0 or count_of_potential_positions > max(REPEAT_COUNTS):
        return _INVALID_DIRECTION
    return probabilities



def determine_probabilities_unknown_direction(probability_sets, fwd_blocks, right_blocks, back_blocks, left_blocks):
    """Returns a probability set for each potential direction, NORTH, EAST, SOUTH, WEST, in that respective order."""
    if probability_sets is None:
        probability_sets = (None, None, None, None)
    north_facing_p  = _valid_probs_check(_determine_probabilities(probability_sets[0], fwd_blocks, right_blocks, back_blocks, left_blocks))
    east_facing_p   = _valid_probs_check(_determine_probabilities(probability_sets[1], left_blocks, fwd_blocks, right_blocks, back_blocks))
    south_facing_p  = _valid_probs_check(_determine_probabilities(probability_sets[2], back_blocks, left_blocks, fwd_blocks, right_blocks))
    west_facing_p   = _valid_probs_check(_determine_probabilities(probability_sets[3], right_blocks, back_blocks, left_blocks, fwd_blocks))
    return (north_facing_p, east_facing_p, south_facing_p, west_facing_p)



def _move_robot_direction(prob, moves_north, moves_east):
    if prob is not _INVALID_DIRECTION:
        ## Y is positive in south direction
        prob = apply_movement_filter(moves_east, -moves_north, prob, ignore_kernel=False)
    return prob



def apply_movement_filter_unknown_direction(probability_sets, moves_fwd, moves_right):
    north_facing_p = _move_robot_direction(probability_sets[0], moves_fwd, moves_right)
    east_facing_p  = _move_robot_direction(probability_sets[1], -moves_right, moves_fwd)
    south_facing_p = _move_robot_direction(probability_sets[2], -moves_fwd, -moves_right)
    west_facing_p  = _move_robot_direction(probability_sets[3], -moves_right, moves_right)
    return (north_facing_p, east_facing_p, south_facing_p, west_facing_p)




def determine_directions(probability_sets) -> tuple[bool, bool, bool, bool]:
    """Returns boolean direction flags."""
    (north_p, east_p, south_p, west_p) = probability_sets
    north_facing = _valid_probs_check(north_p) is not _INVALID_DIRECTION
    east_facing  = _valid_probs_check(east_p)  is not _INVALID_DIRECTION
    south_facing = _valid_probs_check(south_p) is not _INVALID_DIRECTION
    west_facing  = _valid_probs_check(west_p)  is not _INVALID_DIRECTION
    return (north_facing, east_facing, south_facing, west_facing)



def get_probability_set_of_direction(probability_sets, direction_flags: tuple[bool, bool, bool, bool]) -> _np.array:
    """Returns appropriate probability set assuming a direction has been found.
    Only 1 element of direction_flags must be True.
    Raises ValueError.
    """
    if sum(direction_flags) != 1:
        raise ValueError("Too many directions appear to be True!")

    return probability_sets[direction_flags.index(True)]



############
### MAIN ###
############
setup()

## == TESTS ==
if __name__ == '__main__':
    ## == Print to terminal the MAZE ==
    _print_maze()

    ## == See locations of all repeated blocks ==
    # print("Showing all repeated blocks....")
    # for val in REPEATED:
    #     draw(_search_for_tuple(MAZE, val))
    #     input("[ENTER] to continue...\n")
    # print("All repeated blocks have been shown")


    ## == Test determine locations for unknown direction ==
    print("Start at some unknown direction and location, only assuming you are aligned with a wall.")
    prob_sets = determine_probabilities_unknown_direction(None, 0, 0, 3, 0)
    for i, p in enumerate(prob_sets):
        if p is _INVALID_DIRECTION:
            continue
        print(f"Probabilities if robot is facing {DIRECTIONS[i]}")
        draw(p)
        input("[ENTER] to continue...\n")
    print("Now assume you move 1 block forward")
    prob_sets = rotate_90_prob_sets(prob_sets, 2)
    prob_sets = apply_movement_filter_unknown_direction(prob_sets, 1, 0)
    prob_sets = determine_probabilities_unknown_direction(prob_sets, 2, 0, 1, 0)
    for i, p in enumerate(prob_sets):
        if p is _INVALID_DIRECTION:
            continue
        print(f"Probabilities if robot is facing {DIRECTIONS[i]}")
        draw(p)
        input("[ENTER] to continue...\n")

    ## == Test determine locations for KNOWN direction ==
    # probs = determine_probabilities(None, 0, 0, 3, 0)
    # print(f"Potential locations are: {get_locations(probs)}")
    # draw(probs)
    # input("Next... [ENTER]")
    # probs = apply_movement_filter(1, 0, probs)
    # draw(probs)

    # input("Exit... [ENTER]")
else:
    setup()
