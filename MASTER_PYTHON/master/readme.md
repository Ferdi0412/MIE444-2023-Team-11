Ideas:

- Master:
    - Have all top-level stuff in a "\master" directory


- For Centering:
    - Calculate angle required from wall to get to next block center

- For Wall Aligning:
    - Use 2 side sensors on each side??
    - Average if 2 sides
    - "bucket" by for example 5 degrees - no super high accuracy needed
    - Calculate after every 2 inches of movement

- For localizing:
    - Use histogram_distance, but have them be tuples of distances, and if direction estimate not known, estimate 4 directions by running position test 4 times with re-ordered tuple of directions
    - Add option to have distance "cut-off" (ie. max-distance to check for)

- For navigation:
    - In current block:
        - Calculate distance from center of current block based on wall readings...
    - To loading zone:
        - Hardcode in all potential entries to loading zone
        - For each entry, calculate shortest path
        - Select shortest potential paths to any entry
    - To drop-off-zone:
        - Config file with drop-off-zone
        - If drop-off-zone is None, add None, and take input upon run-time

- For block pick-up:
    - Ignore for now...

- For UI:
    - Have all stuff as functions
    - Have a "manual-mode" flag in master code
    - Maybe have settings to change any input params to the rest of the code? (Time-permitting)

- For debugging Serial:
    - Have arduino forward all incoming Serial to Serial3, then listen to bluetooth in
    - Measure power lines when operating robot
