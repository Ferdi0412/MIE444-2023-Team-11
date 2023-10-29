"""Intended for connecting to the actual robot.

Because I struggled with pybluez library (I think some firewall settings are to blame), I am running Serial to an ESP32 board with bluetooth, which is communicating with the robot.
"""

# PyBluez not working on my computer... IDK what I'm doing wrong
# import bluetooth

import serial

import struct

import zmq

import os, sys
sys.path.append(os.path.dirname(__file__))

from get_config import get_config, setup

cfg = get_config()

with open('com-port.txt', 'r') as com_file:
    com_port = com_file.read()

motion = cfg['motion-api']
sensor = cfg['sensor-api']

requires_val = cfg['motion-needs-val']

motion_rev = {value: key for key, value in motion.items()}
sensor_rev = {value: key for key, value in sensor.items()}

class TranslationError (Exception):
    pass

##########################
##### C TYPE HANDLING ####
##########################
def float_to_bytes(val: float) -> bytes:
    """Translate a float value to a byte."""
    return struct.pack('>f', val)

def bytes_to_float(val: bytes) -> float:
    """Translate a float value from bytes."""
    return struct.unpack('>f', val)[0]

def bytes_to_int(val: bytes) -> int:
    return struct.unpack('>i', val)[0]

#######################
#### TRANSLATE MSG ####
#######################
def translate_motion_in(id: str, value: str) -> bytes:
    translated = bytearray([motion[id]])

    if value is not None:
        try:
            translated.extend(float_to_bytes(float(value)))

        except ValueError:
            raise TranslationError

    return bytes(translated)

def translate_in(msg: str) -> str:
    """Translate incoming message for robot"""
    ## Handle linear motion commands/special motion commands
    if msg[0] in motion:
        ## If message doesn't require a value, assign None
        return translate_motion_in(msg[0], msg[1:] if msg[0] in requires_val else None)

    ## Handle rotational motion commands
    elif msg[0:2] in motion:
        return translate_motion_in(msg[0:2], msg[2:])

    match msg:
        case 'SENSORS':
            return bytes([sensor['S']])

        case 'US-ALL':
            return bytes([sensor['U']])

        case 'G':
            return bytes([sensor['G']])

        case _:
            if msg[0:2] == 'US' and len(msg) == 3:
                try:
                    return bytes( [sensor['U']] + int(msg[2]) )

                except ValueError:
                    raise TranslationError

            else:
                raise TranslationError



def translate_rep(msg: bytes) -> str:
    """Translate reply from robot.

    Assumes:
    That all values sent from robot are float...
    TODO: Check the assumption when programming robot.
    """
    return str(bytes_to_float(msg))

class Connections:
    def __init__(self, context: zmq.Context = None, connection: serial.Serial = None):
        self._context = context or zmq.Context()
        self._socket  = setup(self._context)

        self._connection = connection or serial.Serial(com_port, 9600, timeout = 1)

    def main(self):
        try:
            from_user = self._socket.recv()

        except zmq.Again:
            return

        try:
            translated = translate_in(from_user)

        except TranslationError:
            self._socket.send(b'NOT-SUPPORTED')

        ## TODO: Add error handling for serial comms.

        self._connection.write(translated)

        from_machine = self._connection.readline().decode('ascii')

        self._socket.send(translate_rep(from_machine))

    def close(self):
        self._connection.close()


if __name__ == '__main__':
    conn = Connections()

    while True:
        conn.main()
