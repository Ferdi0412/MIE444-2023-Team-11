COM = "COM18"

import serial
import struct

imu = serial.Serial(COM, timeout=1)

class Timeout (Exception):
    pass

# def read_imu():
#     values = imu.readline()
#     if values:
#         return struct.unpack('h', values)

#     else:
#         raise Timeout

# def get_imu():
#     print(imu.write(b'G'))

def read_bytes(bytes_to_read: int) -> bytes:
    bytes_read = bytearray([])
    for i in range(bytes_to_read):
        bytes_read.extend(imu.read())
    return bytes(bytes_read)



def read_imu():
    imu.write(b'U')
    val = imu.read()
    while val != b'U':
        val = imu.read()
        print(val)
        pass

    val = read_bytes(12)

    print(val)

    return struct.unpack('h', val)


while True:
    input("Trigger...")
    read_imu()
