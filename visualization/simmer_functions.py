ultrasonic_list = ['u1', 'u2', 'u3', 'u4', 'u5']

import socket
import struct
import _thread

import math

from threading import Thread

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT_TX = 61200     # The port used by the *CLIENT* to receive
PORT_RX = 61201     # The port used by the *CLIENT* to send data

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
    return res[0]

def forward():
    transmit('xx')
    return transmit('w0-0.5')

def backward():
    transmit('xx')
    return transmit('w0--0.5')

def left():
    transmit('xx')
    return transmit('d0-0.5')

def right():
    transmit('xx')
    return transmit('d0--0.5')

def clockwise():
    transmit('xx')
    return transmit('r0--5')

def counterclockwise():
    transmit('xx')
    return transmit('r0-5')

def is_active():
    return transmit('w0-0') != math.inf

def get_ultrasonics():
    return [transmit(us) for us in ultrasonic_list]
