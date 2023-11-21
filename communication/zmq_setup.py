"""Functions to setup zmq communication sockets.

Requires pyzmq library...


"""

PUBLISHER_PORT = 3001
ROUTER_PORT    = 3002

import zmq
from   zmq import Again as ZmqTimeout
from threading import Thread

def get_subscriber(*, timeout: int = None) -> zmq.Socket:
    """Returns a SUBSCRIBER socket.

    PARAMS:
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> <None>; Blocking behaviour (never times out).
    """
    context = zmq.Context()
    if timeout:
        context.setsockopt(zmq.RCVTIMEO, timeout)
    socket = context.socket(zmq.SUB)
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    socket.connect(f"tcp://127.0.0.1:{PUBLISHER_PORT}")
    return socket

def get_publisher(*, timeout: int = 1000) -> zmq.Socket:
    """Returns a PUBLISHER socket.

    PARAMS:
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> 1000; Times out after 1 second of inactivity.
    """
    context = zmq.Context()
    if timeout:
        context.setsockopt(zmq.RCVTIMEO, timeout)
    socket = context.socket(zmq.PUB)
    socket.bind(f"tcp://127.0.0.1:{PUBLISHER_PORT}")
    return socket

def get_server(*, timeout: int = 1000) -> zmq.Socket:
    """Returns a SERVER socket.

    PARAMS:
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> 1000; Times out after 1 second of inactivity.
    """
    context = zmq.Context()
    if timeout:
        context.setsockopt(zmq.RCVTIMEO, timeout)
    socket = context.socket(zmq.ROUTER)
    socket.bind(f"tcp://127.0.0.1:{ROUTER_PORT}")
    return socket

def get_client(client_id: str, *, timeout: int = None) -> zmq.Socket:
    """Returns a DEALER client socket.

    PARAMS:
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> <None>; Blocking behaviour (never times out).
    """
    context = zmq.Context()
    if timeout:
        context.setsockopt(zmq.RCVTIMEO, timeout)
    socket = context.socket(zmq.DEALER)
    socket.setsockopt_string(zmq.IDENTITY, client_id)
    socket.connect(f"tcp://127.0.0.1:{ROUTER_PORT}")
    return socket
