Requires following python libraries:
- pyserial

```bash
pip install pyserial
```

Import the following class(es):

```python
from robot import NoMotorAck, SingleMotorAck, NoUltrasonics, Team_11_Robot

robot = Team_11_Robot("COMXX")

robot.move_forward(distance_in_inches)

inches_moved = robot.get_progress()
is_in_motion = robot.get_avtive()

robot.stop()

robot.rotate(angle_in_degrees)

(u0, u1, u2, u3, u4, u5) = robot.get_ultrasonics()

robot.set_led(red=255, green=0, blue=0)
time.sleep(1.5)
robot.set_led_off()
```
