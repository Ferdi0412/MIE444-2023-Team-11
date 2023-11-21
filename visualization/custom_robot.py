import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json

from communication.zmq_setup import ZmqTimeout, get_client

RETRIES = 3

client = get_client("Vizualization")

def _get_ultrasonics():
    client.send(b'U')
    msg = client.recv().decode('utf-8')
    print(msg)
    if msg == 'MAX-RETRIES':
        return None
    else:
        values = json.loads(msg)
        values = [values[v] for v in sorted(values.keys())]
    if len(values) >= 5:
        return values[:6]
    else:
        return None

def get_ultrasonics():
    for _ in range(RETRIES):
        readings = _get_ultrasonics()
        if readings is not None:
            return readings
    else:
        raise Exception("Max Retries Reached")

## 3 retries to fetch valid ultrasonic readings
    for _ in range(3):

        if newest_readings is None:
            continue
print(get_ultrasonics())
