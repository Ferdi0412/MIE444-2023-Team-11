from typing import Dict, Iterable, Any, Generator
from time   import sleep
import json

import serial as pyserial

from communication.serial_base import setup_serial, decode_int16, encode_int16, encode_float, EncodingError
# from communication.zmq_setup   import get_server, get_publisher, ZmqTimeout


def parse_ultrasonic_msg(msg: bytes) -> Dict[int, int]:
        readings = {
                i: decode_int16(val_read)[0]
                for i, val_read in enumerate(_slice(msg[1:], 2))
            }
        return readings

def _slice(initial: Iterable[Any], slice_sizes: int) -> Iterable[Iterable[Any]]:
    """Returns iterable slices of initial. Ignores any values that don't match slice_sizes"""
    slices = (len(initial) // slice_sizes)
    for i in range(slices):
        yield(initial[ i*slice_sizes : (i+1)*slice_sizes ])


class MaxRetries(Exception):
    """Raised when expected message not returned withing maximum retries."""

class OurRobot:
    # ultrasonic_count = 6

    def __init__(self, com_port: str, *, com_timeout = 0, recv_retries = 10, retry_sleep = 0.1):
        self.serial = pyserial.Serial(com_port, timeout=com_timeout) #setup_serial(com_port, com_timeout)
        self.recv_retries = recv_retries
        self.retry_sleep = retry_sleep

    def handle_msg(self, msg: bytes) -> None:
        pass

    def transmit(self, msg: bytes) -> None:
        print(f"Transmitting {msg}")
        self.serial.write(msg)

    def _move_motor_cmd(self, motor_id: int, motor_dist: int, motor_speed: float) -> bytes:
        msg = bytearray(b'M')
        if isinstance(motor_id, str):
            motor_id = ord(motor_id)
        msg.append(motor_id)
        msg.extend(encode_int16(motor_dist))
        msg.extend(encode_float(motor_speed))
        return bytes(msg)

    def get_ultrasonic_readings(self) -> Dict[int, int]:
        self.serial.write(b'U')
        overflow = b''
        catch_next = False
        readings = None

        for _ in range(self.recv_retries):
            msgs     = self.serial.readlines()

            for msg in msgs:
                msg = overflow + msg.replace(b'\n', b'').replace(b'\r', b'')
                if msg[0:1] == b'U':
                    readings = readings = { i: decode_int16(val_read, unsigned=True)[0]
                                            for i, val_read in enumerate(_slice(msg[1:], 2)) }
                    overflow   = msg[len(msg[1:])%2:]
                    catch_next = True

                elif catch_next:
                    readings.update({ i: decode_int16(val_read, unsigned=True)[0]
                                      for i, val_read in enumerate(_slice(msg, 2)) })
                    overflow = b''
                    catch_next = False

                else:
                    self.handle_msg(msg)

            if readings and len(readings) == 6:
                return readings

            else:
                sleep(self.retry_sleep)

        if readings is None:
            raise MaxRetries

        else:
            return readings



if __name__ == '__main__':

    robot = OurRobot("COM13", com_timeout=0)
    # robot = OurRobot("COM11", com_timeout=0)


    # server = get_server()

    # while True:
    if input("Send msg [enter]:\n"):
        robot.transmit(b'P\x00')

    # robot.transmit(b'P\x00\x00\x00\x00')

    # robot.transmit(robot._move_motor_cmd(1, 420, 10))

    while True:
        sleep(1)
        msg = robot.serial.read()
        if msg:
            print(msg)
            break

    # while True:
    #     try:
    #         requestor, request = server.recv_multipart()
    #         print(f"[{requestor}] Sent {request}")
    #     except ZmqTimeout:
    #         continue

    #     if request[0:1] == b'U':
    #         print("Replying to ultrasonic request...")
    #         try:
    #             readings = json.dumps(robot.get_ultrasonic_readings()).encode('utf-8')
    #         except MaxRetries:
    #             readings = b'MAX-RETRIES'
    #         print(readings)
    #         server.send_multipart([requestor, readings])
    #     input("Press to read sensors...")
    #     print(robot.get_ultrasonic_readings())
