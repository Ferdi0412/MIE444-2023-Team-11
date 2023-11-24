from connector._encode import encode_forward, encode_active, encode_backwards, encode_clockwise, encode_counter_clockwise, encode_led, encode_progress, encode_ultrasonic

from connector._robot_config import Acknowledges

import serial

ser = serial.Serial("COM13")

print("Connected!")

def send(msg):
    ser.write(msg)
    print(msg)
    return ser.readline()

print(send(encode_forward(10000)))

# while (encode_active() == Acknowledges.ACTIVE):
#     print("Im still standing!")

print(send(encode_ultrasonic()))

# ser.write(encode_backwards())

