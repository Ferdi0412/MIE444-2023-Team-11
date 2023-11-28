Libraries:
* numpy
* scipy
* matplotlib
* networkx

PIP-Installs:
```bash
pip install numpy scipy matplotlib networkx
```

# histogram
```python
from maze import histogram

## Some "config" options are available
histogram.RESOLUTION         = 12   # The number of units per block in maze
histogram.P_HIT              = 0.6  # How probability updates on match
histogram.P_MISS             = 0.2  # How probability updates on miss
histogram.DISTANCE_THRESHOLD = 3    # The maximum distance to match on


## Necessary to generate the maze
histogram.setup()


## Some available "vars"
histogram.REPEATED      # Any repeated reading combinations
histogram.REPEAT_COUNTS # The number of times each .REPEATED is repeated

histogram.DIRECTIONS[i] # Name of given direction, i in [0, 3]


## Can be used for "rotate..." functions, to assign robot heading
histogram.DIRECTIONS.NORTH
histogram.DIRECTIONS.EAST
histogram.DIRECTIONS.SOUTH
hisotgram.DIRECTIONS.WEST


## Get data about tile in map
histogram.distance_any_direction(row, col) # Get thresholded readings of each direction, assuming facing NORTH
histogram.distance_any_direction_raw(row, col) # Same, but unbounded by DISTANCE_THRESHOLD


measurements = histogram.rotate_90(fwd, right, back, left, histogram.DIRECTIONS.EAST) # Rotate measurements to account for robot heading/direction


## LOCALIZING
p = histogram.determine_probabilities(earlier_p, measurements[0], measurements[1], measurements[2], measurements[3]) # Get probability if earlier_p is None, else update given new readings

histogram.draw(p, title=histogram.DIRECTIONS[i]) # Display potential positions

histogram.get_locations(p) # Get probable location in maze

p = histogram.apply_movement_filter(along_columns, along_rows, p) # Update probability

if histogram.is_valid_prob(p): # Check if probability is valid (matters for unkown direction search)
    histogram.draw(p)

p_set = histogram.determine_probabilities_unkown_directions(probability_sets, fwd, right, back, left) # Calculate set of all potential position, given all potential headings

p_set = histogram.apply_movement_filter_unkown_direction(p_set, fwd, right, rotates) # Update given motion of robot. 'rotates' is how many 90 degrees clockwise have occured

direction = determine_direction(p_set)

if direction is not None:
    ## You have now figured out your heading/direction!!!
    ## This will be the heading you had when it was first created

```
