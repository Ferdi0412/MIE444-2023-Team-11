"""Made using tutorial:

"""

import socket
import yaml
import os, sys

curr_dir = os.path.dirname(__file__)
cfg_dir = os.path.join(curr_dir, 'bt-config.yaml')
# sys.path.append(curr_dir)

with open(cfg_dir, 'r') as cfg_file:
    cfg = yaml.safe_load(cfg_file)


MAC_ADDRESS = cfg['MAC-ADDRESS']

CHANNEL = 2

assert len(MAC_ADDRESS) == 17 and MAC_ADDRESS.count(':') == 5

server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

server.bind((MAC_ADDRESS, CHANNEL))

client, addr = server.accept()

try:
    while True:
        client.send(input().encode("ascii"))
except OSError: ## TODO: Change this....
    pass

client.close()
server.close()
