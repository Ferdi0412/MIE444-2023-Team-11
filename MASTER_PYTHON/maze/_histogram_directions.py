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

P_HIT  = 0.6
P_MISS = 0.2

RESOLUTION = 1

#################
### FUNCTIONS ###
#################
def _generate_maze(resolution):
    """Initialize MAZE."""
    maze = _np.array( [[_np.nan] * OPEN.shape[1]] * OPEN.shape[0],
                      dtype = _np.dtype( [('NORTH', '<f4'),
                                          ('EAST', '<f4'),
                                          ('SOUTH', '<f4'),
                                          ('WEST', '<f4')] ) )
    for row in range( 1, maze.shape[0] + 1 ):
        for col in range( 1, maze.shape[1] + 1):
            if WALLS[row, col]:
                maze[row-1, col-1] = tuple([-1, -1, -1, -1,])
                continue

            east  = _np.argmax( WALLS[row, col-1 :: -1] )
            west  = _np.argmax( WALLS[row, col+1 :    ] )
            north = _np.argmax( WALLS[row-1 :: -1, col] )
            south = _np.argmax( WALLS[row+1 :,     col] )

            maze[row-1, col-1] = tuple([north, east, south, west,])
    return _np.repeat( _np.repeat( maze, resolution, axis=1 ), resolution, axis=0 )



def setup():
    global MAZE
    MAZE = _generate_maze(RESOLUTION)



def _search_for_tuple(search_array: _np.array, search_target: tuple) -> _np.array:
    """Returns 'search_array == search_target' when the elements in search_array are tuples."""
    return search_array == _np.array([search_target], dtype = search_array.dtype)



def try_locate_unknown_direction(fwd_blocks, right_blocks, back_blocks, left_blocks):
    """Returns a probability set for each potential direction, NORTH, EAST, SOUTH, WEST, in that respective order."""
    north_facing_p = try_locate(None, fwd_blocks, right_blocks, back_blocks, left_blocks)
    east_facing_p  = try_locate(None, left_blocks, fwd_blocks, right_blocks, back_blocks)
    south_facing_p = try_locate(None, back_blocks, left_blocks, fwd_blocks, right_blocks)
    west_facing_p  = try_locate(None, right_blocks, back_blocks, left_blocks, fwd_blocks)
    return north_facing_p, east_facing_p, south_facing_p, west_facing_p



def try_locate(probabilities: _np.array, north_blocks, east_blocks, south_blocks, west_blocks):
    """If facing NORTH, right becomes EAST."""
    if probabilities is None:
        probabilities = _np.ones( MAZE.shape )

    p_update = _np.ones( MAZE.shape, _np.float64 ) * P_MISS

    p_update[ _search_for_tuple(MAZE, tuple([north_blocks, east_blocks, south_blocks, west_blocks])) ] = P_HIT

    #p_update[ MAZE == 0 ] = 0

    probabilities = _np.multiply(p_update, probabilities)

    probabilities /= _np.sum(probabilities)

    return probabilities



def apply_movement_filter(x_steps: int, y_steps: int, probabilities: _np.array):
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

    probabilities = convolve2d(probabilities, KERNEL, 'same')

    probabilities[ _search_for_tuple( MAZE, tuple([-1, -1, -1, -1]) ) ] = 0

    return probabilities



def get_locations(probabilities: _np.array) -> list[tuple[float, float]]:
    """Get list of (row, col) the robot may currently be in given a probabilities set."""
    return _np.where(probabilities == probabilities.max())



def draw(probabilities: _np.array) -> None:
    """Display a probabilities plot."""
    plt.close()
    plt.matshow(probabilities)
    plt.draw()
    plt.pause(0.001)



def _count_non_unique(some_array: _np.array, resolution: int = 1) -> int:
    """Returns number of non-unique measurements."""
    occurance_counts = _np.unique(some_array, return_counts=True)[1]
    return _np.sum(occurance_counts > resolution)



def _non_unique(some_array: _np.array, resolution: int = 1) -> tuple[_np.array, _np.array]:
    """Return the indices of all non-unique measurements."""
    occ_vals, occ_counts = _np.unique(some_array, return_counts=True)
    return occ_vals[_np.where(occ_counts > resolution)]



############
### TEST ###
############
if __name__ == '__main__':
    setup()

    print(_non_unique(MAZE))

    print(f"There are {_count_non_unique(MAZE)} non-unique tiles in the maze")

    # plt.matshow(MAZE)
    # for row in range(MAZE.shape[0]):
    #     for column in range(MAZE.shape[1]):

    #         probs = try_locate(None, *MAZE[row, column])
    #         draw(probs)
    #         input("Next... [ENTER]")
    # probs = try_locate(apply_movement_filter(0, -1, probs), 2, 0, 1, 0)
    probs = try_locate(None, 3, 0, 0, 0)
    draw(probs)

    input("Exit... [ENTER]")

