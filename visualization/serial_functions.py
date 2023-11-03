COM = "COM9"

import serial

ser = serial.Serial(COM, 9600)

if not ser.isOpen():
    raise Exception("Serial not open!")

def transmit(data):
    ser.write(data + '\r\n')

def receive(data):
    return ser.readline()

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
