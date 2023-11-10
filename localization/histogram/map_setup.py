import numpy as np
import yaml
import os

########################
### READ CONFIG FILE ###
########################
try:
    ## Import config file
    cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
    with open(cfg_path, 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)

    ## Extract important settings
    blocks = cfg['blocks']
    size   = cfg['map-area']
    steps  = cfg['map-increments']

## Two errors that can be expected in case of changes in localization directory
except FileNotFoundError:
    raise FileNotFoundError(f"A file named 'config.yaml' is required...\nCurrently searching direcctory at:\n{cfg_path}")

except KeyError:
    raise KeyError(f"Ensure that all of the following are in {cfg_path}:\n'blocks'; 'map-area'; 'map-increments';")


######################
### SETUP MAZE MAP ###
######################
## Maze has dimensions of maze * steps (ie. scaled by steps for smaller increments...)
maze_mask = np.zeros(size)
maze      = np.zeros(size)

## Assign 1 for each location in the maze where there is a wall (within bounds of maze)
for (x, y) in blocks:
    ## x-1, y-1 such that position "1" is first row/column/whatever.... Indexing thing
    maze_mask[x-1, y-1] = 1
## Pad with walls that define the edges of the maze
maze_mask = np.pad(maze_mask, 1, 'constant', constant_values=1)

## Create internal maze that the robot will navigate
for row in range( 1, size[0] + 1 ):
    for col in range( 1, size[1] + 1 ):
        ## row and col correspond to indexes in maze_mask,
        ## which are 1 greater than the corresponding rows and columns
        ## in maze, due to the padding applied to maze_mask...
        left   = maze_mask[row, col - 1]
        right  = maze_mask[row, col + 1]
        top    = maze_mask[row - 1, col]
        bottom = maze_mask[row + 1, col]

        ## Check if opposites (config 5)
        ## sorry for weird syntax, just did quickly and didn't bother to improve
        top_and_bottom = top and bottom
        left_and_right = left and right
        opposite = (top_and_bottom != left_and_right)

        ## Assign 4 to indicate this is a wall, if appropriate
        if maze_mask[row, col]:
            maze[row-1, col-1] = 4
        ## Assign opposites as 5, otherwise assign number of adjacent walls...
        elif opposite:
            ## row-1, col-1 to account for the padding on maze_mask
            maze[row-1, col-1] = 5
        else:
            ## row-1, col-1 to account for padding applied to maze_mask
            ## apply sum of any left, right, top and bottom walls
            maze[row-1, col-1] = (left + right + top + bottom)


## Expand maze to have the appropriate resolution/increments
maze = np.repeat( np.repeat(maze, steps, axis=1), steps, axis=0 )
