import os, yaml
import zmq

def get_config():
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    return cfg

def setup(context: zmq.Context = None) -> zmq.Socket:
    """Sets up socket for connections."""
    context = context or zmq.Context()
    interface = context.socket(zmq.REP)
    interface.setsockopt(zmq.RCVTIMEO, 1_000)
    interface.bind(f"tcp://*:{PORT}")
    return interface
