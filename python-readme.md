# Simmer Requirements
For Simmer, the following version of python is required:
```bash
python --version # Should equal 3.11 or greater

## OR

python3 -- version # Should be 3.11 or greate
```

Default libraries needed:
```bash
pip install pygame numpy shapely
```

Note that pygame should be version 2.5 or greater
```python
import pygame

pygame.__version__ >= '2.5.0'
```

# Robot Control Requirements
To interface with the robot, you need the following libraries:
- [PyYaml](https://github.com/yaml/pyyaml)
- [ZeroMQ](https://zeromq.org/)
- [PySerial](https://pyserial.readthedocs.io/en/latest/pyserial.html)
<br>**Installation:**
```bash
pip install pyyaml pyzmq pyserial
```
<br>**Importing:*
```python
import yaml
import zmq
import serial
```

# Recommendation (Zero MQ)
I (Ferdi) recommend using a library called [Zero MQ (zmq)](https://zeromq.org/) when making several python processes/programs run simultaneously, for communication between each other.
<br>It has extensive support, and is easy to use, and has many [Python examples](https://zeromq.org/languages/python/). Highly recommend checking it out!
```bash
pip install zmq
```
The basic connection types are the Requestor-Replier (zmq.REQ, zmq.REP) types. Here, severl requestors can connect to a single replier.
```python
import zmq

## Setting up a Replier/Receiver type connection
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*3000")

msg = socket.recv()
print(f"Received message: {msg}") ## eg. "Received message: Hello World"
socket.send("Response!")

## Setting up a Requestor/Sender/Client type connection
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:3000")

socket.send(b"Hello World")
msg = socket.recv()
print(f"Responded with: {msg}") ## eg. "Responded with: Response!"
```

# Recommendation (Miniconda)
I (Ferdi) recommend setting up a conda environment, as I find this easier to use, especially if you want several projects on the same computer. An environment is essentially an isolated "setup", and conda is a tool for controlling python enironments.
<br><br>There are several versions of conda, notably Miniconda and Anaconda. Anaconda is big and comes with many tools, whilst Miniconda solely provides command-line access to conda.
<br><br>**Miniconda setup**

1. Download and follow the installation for [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/).

2. Ensure you have access to conda from the command line (Command Prompt in Windows, terminal on Apple). If you do not have access, but you have installed it, check that you have your [PATH](https://superuser.com/questions/284342/what-are-path-and-other-environment-variables-and-how-can-i-set-or-use-them) environment variable set. To check, run the following in the command line:
```bash
conda --version
```

3. Set up a conda environment:
```bash
conda create -n "MIE444-Project"
```

4. Activate your conda environment (note that this makes the conda environment "active" and available in the current command line session, ie. you will have to re-activate the environment for every Command Prompt window you open):
```bash
conda activate "MIE444-Project"
```

5. Install [pip](https://realpython.com/what-is-pip/) package/library management tool:
```bash
conda install pip
```

6. Install the necessary libraries, for example to install the simmer packages:
```bash
# Using pip you can install several libraries/packages at once
# The following line will install the most recent versions of numpy and shapely packages:
pip install numpy shapely

# You can also control the version of the library installed:
pip install pygame = 2.5 # This is just an example, as long as pygame is 2.5 or greater you should be fine
```

# Recommendation (VsCode)
I (Ferdi) recommend using [VsCode](https://code.visualstudio.com/) as the main IDE for development.
<br>[NOTE] Make sure you have the correct *Python Interpreter* when running files.

1. With a python folder open, press \<CTRL + SHIFT + p\>

2. Type in/select "Python: Select Interpreter"

3. Select the appropriate environment. This will be similar to "Python 3.11.x ('MIE444-Project')..." if you followed the Miniconda setup above.

4. When running python code, I also recommend using the "Run Python File in Dedicated Terminal" option when running python from VsCode.
![Img](https://code.visualstudio.com/assets/docs/python/tutorial/debug-python-file-in-terminal-button.png)
*Image taken from [Getting Started with Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)*
