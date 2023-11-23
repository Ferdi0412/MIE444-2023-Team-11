## IDs of motors
MOTOR_LEFT  = b'\x02'
MOTOR_RIGHT = b'\x03'

MOTOR_LEFT_FACTOR  = 0.96 ## To account for right-bias
MOTOR_RIGHT_FACTOR = 1.0
MOTOR_SPEED_MAX    = 100

## Number of pulses per inch fwd
PULSES_FWD = 100

## Number of pulses per 90 degrees of rotation
PULSES_ROT =  50

## Arduino uses a 2 byte int size
SIZEOF_CHAR  = 1
SIZEOF_INT   = 2
SIZEOF_FLOAT = 4

## Ultrasonic readings order
ULTRASONIC_ORDER = ['U0', 'U1', 'U2', 'U3', 'U4', 'U5'] # ['FL', 'FR', 'R', 'B', 'L']
ULTRASONIC_COUNT = len(ULTRASONIC_ORDER)

## Expected message lengths
## First  SIZEOF_CHAR is for the message "ID"
## Second SIZEOF_CHAR is for motor "ID" (for progress and active)
## Third/Second SIZEOF_CHAR is for the end '\n'
MSG_LEN_PROGRESS   = (3 * SIZEOF_CHAR) + (SIZEOF_INT)
MSG_LEN_ACTIVE     = (3 * SIZEOF_CHAR) + (SIZEOF_INT)
MSG_LEN_ULTRASONIC = (2 * SIZEOF_CHAR) + (ULTRASONIC_COUNT * SIZEOF_INT)
