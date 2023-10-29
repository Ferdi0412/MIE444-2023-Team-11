"""Developed from the dead_reckonging.py script under simmer-python-main/scripts."""

import zmq
import json

import os, sys
## Allow files in this directory to be used...
sys.path.append(os.path.dirname(__file__))

from get_config import get_config

import socket
import struct
import _thread

import math

### Network Setup ###
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT_TX = 61200     # The port used by the *CLIENT* to receive
PORT_RX = 61201     # The port used by the *CLIENT* to send data


## ZMQ port
cfg = get_config()
PORT        = cfg['interface-port']
ULTRASONICS = cfg['simmer-sensors']['us']
GYRO        = cfg['simmer-sensors']['gyro']
COMPASS     = cfg['simmer-sensors']['comp']
SENSORS     = tuple(list(ULTRASONICS) + [GYRO, COMPASS])
NAMES       = cfg['simmer-to-act']
NAMES_REV   = {value: key for key, value in NAMES.items()}

print(NAMES_REV)

def bytes_to_list(msg):
    num_responses = int(len(msg)/8)
    data = struct.unpack("%sd" % str(num_responses), msg)
    return data

class NoConnection (Exception):
    pass

def transmit(data):
    """Sends data to simmer, and returns response."""
    print(f"Sending {data}")
    err = False
    ## TX
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT_TX))
            s.send(data.encode('utf-8'))
        except (ConnectionRefusedError, ConnectionResetError, TimeoutError, EOFError):
            #_thread.interrupt_main()
            err = True
    if err:
        raise NoConnection

    ## RX
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
            try:
                #while True:
                    s2.connect((HOST, PORT_RX))
                    res_raw = s2.recv(1024)
                    if res_raw:
                        print(f"|- Received response from simulator: {res_raw}")
                        res = bytes_to_list(res_raw)
                        print(f"|- Decoded to: {res}")
                        break
            except (ConnectionRefusedError, ConnectionResetError, TimeoutError):
                #_thread.interrupt_main()
                err = True
        if err:
            raise NoConnection

    ## Response received...
    return res

class TranslationError (Exception):
    pass

def move(direction: str, dist: str) -> str:
    """Send a movement command to SIMMER"""
    raw_res = transmit(f"{direction}-{dist}")
    return '' if raw_res[0] == math.inf else 'FAIL'

def translate(msg: str) -> str:
    """Translates received message to the appropriate message in Simmer.
    Raises TranslationError.
    """
    match msg[0]:
        case 'F':
            distance = str(msg[1:])
            return move('w0', distance)


        case 'B':
            distance = str(msg[1:])
            return move('w0-', distance)

        case 'L':
            distance = str(msg[1:])
            return move('d0', distance)

        case 'R':
            distance = str(msg[1:])
            return move('d0-', distance)

        case 'M':
            return move('w0', '0') == 'FAIL'

        case 'H':
            transmit('xx')
            return ''

        case 'P':
            return 'NOT YET IMPLEMENTED!'

        case 'U':
            if msg == 'US-ALL':
                responses = {NAMES[sensor]: transmit(sensor)[0] for sensor in ULTRASONICS}
                return json.dumps(responses)

            elif msg[1] == 'S' and msg[2:] in NAMES_REV:
                return str(transmit(NAMES_REV[msg[2:]])[0])

            else:
                raise TranslationError

        case 'G':
            return str(transmit(GYRO)[0])

        case 'C':
            return str(transmit(COMPASS)[0])

        case 'S':
            ## Both rotation and SENSOR starts with 'S'
            if msg == 'SENSORS':
                responses = {NAMES[sensor]: transmit(sensor)[0] for sensor in SENSORS}
                return json.dumps(responses)

            elif msg[1] == 'L':
                # Counter-clockwise
                angle = str(msg[2:])
                return move('r0-', angle)

            elif msg[2] == 'R':
                # Clockwise
                angle = str(msg[2:])
                return move('r0', angle)

            raise TranslationError

        case _:
            raise TranslationError


##############
##   MAIN   ##
if __name__ == '__main__':
    context = zmq.Context()
    interface = context.socket(zmq.REP)
    interface.setsockopt(zmq.RCVTIMEO, 1000)
    interface.bind(F"tcp://*:{PORT}")

    print("Ready to accept messages!")
    while True:
        try:
            message = interface.recv()
            print(f"Received message: {message}")
            try:
                response = translate(message.decode('utf-8'))
                print(f"|- Response returned: {response}\n")
                interface.send(response.encode('utf-8'))

            except NoConnection as exc:
                print("|- [NoConnection]")
                interface.send(b'NO-CONNECTION')

            except TranslationError:
                interface.send(b"NOT-SUPPORTED")

            except:
                interface.send(b'FATAL-ERROR')

        except zmq.Again:
            pass ## Timeout on recv call, to allow KeyboardInterrupt...
