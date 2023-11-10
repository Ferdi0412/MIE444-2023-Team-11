## Seemingly robust way to import from local folder
import os, sys
sys.path.append(os.path.dirname(__file__))

from map_setup import maze
from measurement import measure
from movement import move

import matplotlib.pyplot as plt

probs = measure(2, None, maze)

probs = move(-3, 0, probs)

print(probs)

plt.matshow(probs)
plt.show()
