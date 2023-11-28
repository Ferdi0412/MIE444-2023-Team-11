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

TIME_OFFSET       = 125 # 80
TIME_TO_DIST      = 10000 / 73 * 1 / 5 * 4
TIME_ANGLE_OFFSET = 145
TIME_TO_ANGLE     = 40 / 2.85 / 1.37 / 1.45 * 7.2 / 6 * 90 / 110

# ULTR_LOOKUP = {"0": "F",
#                "1": "FR",
#                "2": "BR",
#                "3": "B",
#                "4": "BL",
#                "5": "BR",}
