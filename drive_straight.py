import struct, serial

ser = serial.Serial("COM12", timeout=1)

def encode_int(val):
    return struct.pack('<h', val)

def encode_float(val):
    return struct.pack('<f', val)

def _go_fwd(id):
    msg_ = bytearray(b'M')
    msg_.append(id)
    msg_.extend(encode_int(10000))
    msg_.extend(encode_float(60))
    msg_.append(ord(' '))
    return msg_

def go_fwd():
    msg = b''
    for i in range(4):
        msg += _go_fwd(i)
        print(msg)
    ser.write(msg)
    # return msg

print(go_fwd())


while True:
    print(ser.readline())
