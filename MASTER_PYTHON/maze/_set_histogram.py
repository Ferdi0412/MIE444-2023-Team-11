"""Histogram, but everything uses sets to check positions."""
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

RESOLUTION = 12

#################
### FUNCTIONS ###
#################
def _generate_MAZE(resolution):
    """Initialize MAZE."""
    global MAZE
    maze = _np.zeros( OPEN.shape, dtype=_np.object_ )
    for row in range( 1, maze.shape[0] + 1 ):
        for col in range( 1, maze.shape[1] + 1):
            if WALLS[row, col]:
                continue

            east  = _np.argmax( WALLS[row, col-1 :: -1] )
            west  = _np.argmax( WALLS[row, col+1 :    ] )
            north = _np.argmax( WALLS[row-1 :: -1, col] )
            south = _np.argmax( WALLS[row+1 :,     col] )

            maze[row-1, col-1] = set([east, west, north, south])
    MAZE = _np.repeat( _np.repeat( maze, resolution, axis=1 ), resolution, axis=0 )



def setup():
    _generate_MAZE(RESOLUTION)



def try_locate(probabilities: _np.array, fwd_blocks, right_blocks, back_blocks, left_blocks):
    if probabilities is None:
        probabilities = _np.ones( MAZE.shape )

    p_update = _np.ones( MAZE.shape, _np.float64 ) * P_MISS

    p_update[ MAZE == set([fwd_blocks, right_blocks, back_blocks, left_blocks])] = P_HIT

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

    probabilities[ MAZE == 0 ] = 0

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



############
### TEST ###
############
if __name__ == '__main__':
    _generate_MAZE(3)

    # draw(WALLS[1:-1,1:-1])
    # input("Next... [ENTER]")

    # print(MAZE)
    # plt.matshow(MAZE)
    probs = try_locate(None, 0, 0, 3, 5)
    draw(probs)
    input("Next... [ENTER]")
    probs = try_locate(apply_movement_filter(3, 0, probs), 0, 0, 1, 4)
    probs = try_locate(apply_movement_filter(3, 0, probs), 0, 0, 1, 4)
    draw(probs)
    print(get_locations(probs))
    input("Exit... [ENTER]")

