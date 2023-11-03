"""Intended for use to communicate with one of the "middle-man" scripts in this directory.

"""

import zmq
import json

import os, sys
## Allow files in this directory to be used...
sys.path.append(os.path.dirname(__file__))

from get_config import get_config

class RobotTimeout (Exception):
    pass

class RobotContol:
    def __init__(self, timeout_ms: int = 1_000):
        self._context = zmq.Context()
        self._socket  = self._context.socket(zmq.REQ)
        self._socket.setsockopt(zmq.RCVTIMEO, 1000)

        print("RobotControl instance created!")

        self._cfg = get_config()
        self._port = self._cfg['interface-port']

    def connect(self):
        self._socket.connect(f"tcp://localhost:{self._port}")
        print("Connected!")
        return self

    def send_recv(self, message: str):
        try:
            self._socket.send(message.encode('utf-8'))
            res = self._socket.recv().decode('utf-8')

            ## TODO: Fix following round-about way to avoid decoding stuff like 'nan'
            try:
                return json.loads(res)

            except json.decoder.JSONDecodeError:
                return res

        except zmq.Again as exc:
            raise RobotTimeout from exc


if __name__ == '__main__':
    robot = RobotContol().connect()

    while True:
        try:
            response = robot.send_recv(input("Type message:\n"))
            print(f"Responded with: {response}")
        except Exception:
            pass