"""Implementation of HISTOGRAM_2D as presented in lecture."""
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
MASK = _np.pad( OPEN, 1, 'constant', constant_values=0 )
MAZE = _np.zeros(OPEN.shape)

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
    """resolution := how many increments per block in maze."""
    global MAZE
    maze = _np.zeros( OPEN.shape )
    for row in range( 1, maze.shape[0] + 1 ):
        for col in range( 1, maze.shape[1] + 1):
            east   = not MASK[row, col - 1]
            west   = not MASK[row, col + 1]
            north  = not MASK[row - 1, col]
            south  = not MASK[row + 1, col]

            if not MASK[row, col]:
                maze[row-1, col-1] = 0

            elif not any([east, west, north, south]):
                maze[row-1, col-1] = 4

            elif ((north == south) and (east == west)): ## opposites:
                maze[row-1, col-1] = 5

            else:
                maze[row-1, col-1] = 4 - sum([east, west, north, south])
    MAZE = _np.repeat( _np.repeat( maze, resolution, axis=1 ), resolution, axis=0 )


def setup():
    _generate_MAZE(RESOLUTION)




def check_position(front, right, back, left) -> int:
    """Pass in sensor readings."""
    if not any([front, right, left, back]):
        return 4

    elif (front == back) and (left == right):
        return 5

    else:
        return sum([front, left, back, right])



def try_locate(position: int, probabilities: _np.array) -> _np.array:
    """Update probabilities array. MEASURE step of histogram."""
    if probabilities is None:
        probabilities = _np.ones( MAZE.shape )

    p_update = _np.ones( MAZE.shape, _np.float64 ) * P_MISS

    p_update[ MAZE == position ] = P_HIT

    #p_update[ MAZE == 0 ] = 0

    probabilities = _np.multiply(p_update, probabilities )

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
    # print(MAZE)
    # plt.matshow(MAZE)
    probs = try_locate(2, None)
    draw(probs)
    input("Next... [ENTER]")
    probs = try_locate(3, apply_movement_filter(1, 0, probs))
    draw(probs)
    print(get_locations(probs))
    input("Exit... [ENTER]")

