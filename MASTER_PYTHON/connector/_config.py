class Acknowledges:
    W_ACK    = b'W-ACK'
    S_ACK    = b'S-ACK'
    Q_ACK    = b'Q-ACK'
    E_ACK    = b'E-ACK'
    LED_ACK  = b'LED-ACK'
    STOP_ACK = b'STOP-ACK'
    GRIP_ACK = b'GRIP-ACK'
    ACTIVE   = b'ACTIVE'
    NACTIVE  = b'NOT-ACTIVE'

PROG_PREFIX = b'P_'
ULTR_PREFIX = b'U_'

DATA_PREFIX = b'~'

TIME_OFFSET   = 80
TIME_TO_DIST  = 10000 / 72.5
TIME_TO_ANGLE = 1

ULTR_LOOKUP = {"0": "FL",
               "1": "FR",
               "2": "R",
               "3": "B",
               "4": "L",
               "5": "G"}
