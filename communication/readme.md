# Communication with robot
This folder contains python scripts and functions for communicating with/controlling the robot.

# Server.py
This script establishes a server that communicates with the robot, and exposes ZeroMQ sockets for other programs to communicate with.

## Requests
...
<br>[NOTE] Every Client instance MUST have a unique identifier! Ideally there should only be 1 at a time...

```python
## Importing robot client
from communciation import Client

## Initializing client
client = Client(unique_identifier)

## Claim ownership of robot (to enable movements and such)...
try:
    client.claim_ownership():
except:
    ## Handle claim_ownership failure here
    ...

## Check ownership over robot (to check if movements from here are supported)...
## high_priority=True is reserved for main Automation/control code, and will over-write
## the ownership of other Clients
if not client.is_owner():
    client.claim_ownership(high_priority=True)

## Check if another client owns robot
if not client.is_owned():
    client.claim_ownership()

## Revoke ownership
if client.is_onwer():
    client.revoke_own()

## Store position and orientation found from localization
client.store_position(x = x, y = y)
client.store_orientation(orientation = orientation)

## Get position of robot
pos    = client.get_position()
orient = client.get_orientation()
if (pos is None) or (orient is None):
    print("Robot not yet localized...")
else:
    ## Unpack pos to get x and y terms
    x, y = pos

# Move robot forwards by 1 inch, and left by 1 inch (or right by NEGATIVE 1 inch)
if not client.move(fwd=1, right=-1):
    raise Exception("Could not send motion command!")

## Rotate robot clockwise by 90 degrees
if not client.rotate(angle=90):
    raise Exception("Could not send rotate command!")

## Turn on/off LED on robot
if not client.led_on():
    raise Exception("Could not send LED command!")

if not client.led_off():
    raise Exception("Could not send LED command!")

## Wait for robot to stop previous motion, then send move-right command
while client.in_motion():
    pass
client.move(fwd=0, right=1)

## Check progress on each individual motor
for motor_id, motor_progress in ( client.progress() ).items():
    print(f"Motor {motor_id} has progress of {motor_progress:.2f}")

## Check worst-progress, as an indicator for overall progress
print(f"Robot progress on last move/rotate command is: {client.progress_all()}")

## Stop robot, and check that it was successful
progress = client.stop()
if progress is None:
    raise Exception("Robot could not be stopped!")
else:
    print(f"Robot stopped after making {progress} progress from last movement/rotation command!")

## Check ultrasonic readings for each sensor
for sensor_id, sensor_reading in ( client.ultrasonic() ).items():
    print(f"Ultrasonic sensor {sensor_id} read {sensor_reading:.2f} inches")

## Check gyroscope readings
for motion_type, value in ( client.gyroscope() ).items():
    printf(f"Robot IMU reading along {motion_type} was {value}")

```

## Async/subscription based read-only
...

```python
from communication import SubClient

## Initializing client and starting it in seperate thread
client = SubClient()
client.start()

## Get latest ultrasonic reading
latest_reading = client.ultrasonics[sensor_id]

## Get latest updated timestamp for ultrasonics
last_read_timestamp = client.timestamp_ultrasonics

## Get latest progress
latest_progress = client.progress

## Get timestamp of latest_progress
last_prog_timestamp = client.timestamp_progress

## Get current motion status
in_motion = client.in_motion

## Get timestamp of latest in_motion update
last_motion_timestamp = client.timestamp_in_motion

```

# APIs
## Sockets/Internal
### Robot Messaging
| 'Header' | Additional Data | Response Format | Description/Notes |
| :------: | :-------------: | :-------------: | :---------------- |
| MOVE     | \<tuple> [FWD \<float>, RIGHT \<float>,] | \<bool> ACK/UNACK | Sends command to move forward by FWD inches, and right by RIGHT inches. Both values can be negative, to move in opposite direction(s). |
| ROTATE   | \<float> ANGLE   | \<bool> ACK/UNACK       | Sends command to rotate CLOCKWISE by ANGLE degrees. Negative values are COUNTERCLOCKWISE degrees. |
| IN-MOTION | void     | \<bool> is_in_motion  | Returns whether robot is currently moving. |
| PROGRESS  | void     | \<dict> {motor_id \<str>: motor_progress \<float>} | Returns a dictionary representing how far each motor is towards it's goal. |
| PROGRESS-ALL | void | \<float> robot_progress | Returns worst progress (ie. lowest motor_progress from PROGRESS). |
| STOP     | void            | <float | None> robot_progress | Sends command to stop last motion from robot. Returns same value as PROGRESS-ALL at moment of stopping, IFF successful. Otherwise None is returned. |
| LED      | \<bool> On/Off  | \<bool> ACK/UNACK | Turn LED on/off.
| ULTRASONIC | void          | \<dict> {sensor_id \<str>: sensor_reading \<float>} | Request ultrasonic sensor readings, values returned are in inches. |
| GYROSCOPE  | void    | \<dict> {motion_type \<str>: value \<float>} | Returns gyroscope readings in each direction. |
| COMPASS [*NA*]    | void    | \<float> orientation | Returns compass reading. |

### Server
| 'Header' | Response Format | Errors | Description/Notes |
| :------: | :-------------: | :----: | :---------------- |
| CLAIM-OWN | void           | AlreadyOwned | Claim ownership, for certain rights, such as setting motion commands. PARAMS: high_priority \<bool>; |
| IS-OWNER  | \<bool> is_owner | -     | Check if this client owns the robot. |
| HAS-OWNER | \<bool> has_owner | -    | Check if this client has an owner (does not check who owns it). |
| REV-OWN   | void           | -      | Revoke ownership of the robot client. |

### Localization
| 'Header' | Additional Data | Response Format | Errors | Description/Notes |
| :------: | :-------------: | :-------------: | :----: | :---------------- |
| SET-POS  | \<dict> {"x": x_pos \<float>, "y": y_pos \<float>} | void | Unauthorized | Set position of robot in maze using automation. |
| GET-POS  | void            | \<dict \| None> {"x": x_pos \<float>, "y": y_pos \<float>} | void | Get position of robot in maze. |
| SET-ORIENT | orientation \<float> | void | Unauthorized | Set angle/orientation of robot within maze. |
| GET-ORIENT | void            | \<float \| None> orientation | Get the orientation of robot within maze. |

## Robot
When going to/from robot, use single byte/char to indicate target.

### To Robot
**Motion**
| Target | Data [bytes] | Description/Notes |
| :----: | :----------: | :---------------- |
| M      | [1]: ID; [2, 5]: Position \<float>; [6, 9]: Speed \<float>; | Movement command (used for both MOVE and ROTATE). To simplify, send a message to each motor seperately.              |
| S      | NA           | Stop.             |
| P      | [1]: ID;     | Fetch Progress.   |
| A      | [1]: ID;     | "Active" - IN-MOTION. |
| L      | [1]: On/Off; | Turn LED on/off.  |

**Sensors**
| Target | Data | Description/Notes |
| :----: | :--: | :---------------- |
| U      | NA   | Fetch all ultrasonic readings. |
| G      | NA   | Fetch all gyroscope readings. |

### From Robot
**Motion**
| Target | Data | Description/Notes |
| :----: | :--: | :---------------- |
| M      | [1]: ID; [2, 5]: Progress \<float>?; | Acknowledge motion command received. |
| S      | [1]: ID; [2, 5]: Progress \<float>?; | Acknowledge stop command received by motor. |
| P      | [1]: ID; [2, 5]: Progress \<float>; | Progress of a given motor. |
| A      | [1]: ID; [2]: in_motion \<bool>; | If a motor is in motion (true), or stopped (false). |

**Sensors**
| Target | Data | Description/Notes |
| :----: | :--: | :---------------- |
| U      | [1]: ID; [2, 5]: Distance \<float>; | Readings of each individual sensor. |
| G      | [1]: Measure_ID; [2, 5]: reading \<float>; | Readings of each measurement from IMU. |
