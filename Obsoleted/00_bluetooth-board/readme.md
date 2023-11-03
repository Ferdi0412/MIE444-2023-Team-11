# Intention
Add stuff for the seperate ESP32 for use with bluetooth here...

# Libraries

## Yaml
For *.yaml* config file.
```bash
pip install pyyaml
```

```python
import yaml
```

## PyBluez
For bluetooth connections. Weird pip install due to [PyPi issues](https://github.com/pybluez/pybluez/issues/431#issuecomment-1107884273).
```bash
pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
```

```python
import bluetooth
```

## Zero MQ
I intend to expose the data via. [Zero MQ](https://zeromq.org/).
```bash
pip install zmq
```

```python
import zmq
```