"""Functions for working with ZMQ -> Essentially sockets but easier to use!"""
import zmq as _zmq

SocketTimeout = _zmq.Again

def get_subscriber(port: int, *, timeout: int = None) -> _zmq.Socket:
    """Returns a SUBSCRIBER socket.

    PARAMS:
    |- port <int>:
    |    Port to setup subscriber on.
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> <None>; Blocking behaviour (never times out).
    """
    context = _zmq.Context()
    if timeout:
        context.setsockopt(_zmq.RCVTIMEO, timeout)
    socket = context.socket(_zmq.SUB)
    socket.setsockopt_string(_zmq.SUBSCRIBE, '')
    socket.connect(f"tcp://127.0.0.1:{port}")
    return socket

def get_publisher(port: int, *, timeout: int = 1000) -> _zmq.Socket:
    """Returns a PUBLISHER socket.

    PARAMS:
    |- port <int>:
    |    Port to setup publisher on.
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> 1000; Times out after 1 second of inactivity.
    """
    context = _zmq.Context()
    if timeout:
        context.setsockopt(_zmq.RCVTIMEO, timeout)
    socket = context.socket(_zmq.PUB)
    socket.bind(f"tcp://127.0.0.1:{port}")
    return socket

def get_server(port: int, *, timeout: int = 1000) -> _zmq.Socket:
    """Returns a SERVER socket.

    PARAMS:
    |- port <int>:
    |    Port to setup server on.
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> 1000; Times out after 1 second of inactivity.
    """
    context = _zmq.Context()
    if timeout:
        context.setsockopt(_zmq.RCVTIMEO, timeout)
    socket = context.socket(_zmq.ROUTER)
    socket.bind(f"tcp://127.0.0.1:{port}")
    return socket

def get_client(port: int, client_id: str, *, timeout: int = None) -> _zmq.Socket:
    """Returns a DEALER client socket.

    PARAMS:
    |- port <int>:
    |    Port to setup client on.
    |- client_id <str>:
    |    Unique client for given server.
    |- [timeout] <int>:
    |    Milliseconds timeout, or <None> for blocking. Determines timeout for .recv() and similar methods.
    |    If a timeout occurs in a .recv() call, a zmq.Again exception is raised.
    |    [default] -> <None>; Blocking behaviour (never times out).
    """
    context = _zmq.Context()
    if timeout:
        context.setsockopt(_zmq.RCVTIMEO, timeout)
    socket = context.socket(_zmq.DEALER)
    socket.setsockopt_string(_zmq.IDENTITY, client_id)
    socket.connect(f"tcp://127.0.0.1:{port}")
    return socket
