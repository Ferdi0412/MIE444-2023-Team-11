"""

"""
import sys, os
import yaml
import bluetooth as bt

############################
###        CONFIG        ###
with open(os.path.join(os.path.dirname(__file__), 'bt-config.yaml'), 'r') as cfg_file:
    cfg = yaml.safe_load(cfg_file)

MAC_ADDR = cfg['mac-address']

PORT = 1 # cfg['port']

# bt_available = {name: addr for addr, name in bt.discover_devices(lookup_names=True)}

# print(bt_available)

###########################
###      BT SERVER      ###
bt_sock = bt.BluetoothSocket( bt.RFCOMM )
bt_sock.bind((MAC_ADDR, PORT))

bt_sock.close()
