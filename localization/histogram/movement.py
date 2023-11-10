import numpy as np
from scipy.signal import convolve2d

kernel = np.array([[0.1, 0.1, 0.1],
                   [0.1, 0.8, 0.1],
                   [0.1, 0.1, 0.1]])

def move(x_steps: int, y_steps: int, probs: np.array, *, kernel_: np.array = None):
    """Execute a movement convolution on map, after moving by x_steps and y_steps along either axis."""
    ## Allow manual optional kernel input, otherwise use above kernel as default...
    kernel_ = kernel_ or kernel

    probs = np.copy(probs)

    ## Move rightwards/leftwards (across columns)
    if x_steps > 0:
        probs[:, x_steps:]  = probs[:, :-x_steps]
        probs[:, :x_steps] = 0

    elif x_steps < 0:
        probs[:, :x_steps] = probs[:, (-x_steps):]
        probs[:, x_steps:]  = 0

    ## Move upwards/downwards (across rows)
    if y_steps > 0:
        probs[y_steps:, :]  = probs[:-y_steps, :]
        probs[:-y_steps, :] = 0

    elif y_steps < 0:
        probs[:-y_steps, :] = probs[y_steps:, :]
        probs[y_steps:, :]  = 0

    ## Apply convolution to simulate errors...
    probs = convolve2d(probs, kernel_, 'same')

    return probs