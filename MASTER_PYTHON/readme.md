# Sub-directories:

## /automation
Automation of robot, to be implemented.



## /connector
Serial control of robot. Setup works well with Windows, should work with Apple (just the serial com port is different syntactically).

```bash
pip install pyserial pyyaml
```

```python
from connector import Team_11_Robot

robot = Team_11_Robot(COM, 2) # 2 seconds read serial timeout

robot.rotate(90)

robot.move_forward(12)

robot.led(255, 255, 255)

robot.led_off()

print("Robot is active!" if robot.is_active() else "Robot is not moving.")

print(f"{robot.progress() * 100:.0f}% progress along latest move_forward command.")

print(robot.ultrasonic()) # Single reading from each sensor

print(robot.ultrasonic_json(5)) # 5 readings from each sensor
```

## /maze
Localization and navigation of maze.

- histogram (setup for after aligning and orientating)
= histogram_distance (setup for after aligning and orientating)
- pathfinding (setup for localizing)

```bash
pip install pygame numpy scipy matplotlib networkx
```

```python
from maze import histogram

front, right, back, left = robot_detect_walls(...)

tile_type = histogram.check_position(front, right, back, left)

probability = historam.try_locate(tile_type, None)

inches_north, inches_south = robot_move(...)

probability = histogram.apply_movement_filter(inches_nort, inches_south, probability)

front, right, back, left = robot_detect_walls(...)

tile_type = histogram.check_position(front, right, back, left)

probability = histogram.try_locate(tile_type, probability)

histogram.draw(probability)



from maze import pathfinding

pathfinding.setup()

for i, (row, col) in enumerate(pathfinding.get_shortest_path((0, 0), (3, 7))):
    print(f"Step {i} -> Go to ({row}, {col})")
```

## /user_interface
Graphic display and user inputs for robot.

```bash
pip install pandas
```
