import os, sys
sys.path.append(os.path.dirname(__file__))

from interface import RobotContol, RobotTimeout

## TODO: Figure out why perfect performance when running to_simmer seperately, compared to using SimmerConnection().start()
from to_simmer import SimmerConnection
