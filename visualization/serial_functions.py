COM = "COM9"

import serial

from threading import Thread

import time

ser = serial.Serial(COM)

time.sleep(5) ## Cause the bloody serial.Serial takes ages, and is tricky

if not ser.isOpen():
    raise Exception("Serial not open!")

def transmit(data: str):
    print("Transmitting:", (data).encode('utf-8'))
    ser.write((data).encode('utf-8'))

def receive(blocking = True) -> bytes:
    if blocking:
        return ser.readline()
    else:
        return ser.readline(ser.in_waiting)

def forward():
    transmit('w')

def backward():
    transmit('s')

def left():
    transmit('a')

def right():
    transmit('d')

def clockwise():
    transmit('e')

def counterclockwise():
    transmit('q')

def get_ultrasonics():
    transmit('u')
    recv_raw = receive()
    recv_raw = recv_raw.decode('ascii')
    recv = recv_raw.replace('\r', '').replace('\n', '')
    return [0, 0, 0, 0, 0]
    return [int(val) for val in recv.split(';')]

if __name__ == '__main__':
    print("Now in main...")
    ser.read_all()
    print("Writing now...")
    ser.write(b'I\x00\x00\x00\x00')
    print("Reading now...")
    print(ser.read())
