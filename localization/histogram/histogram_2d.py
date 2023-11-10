## Seemingly robust way to import from local folder
import os, sys
sys.path.append(os.path.dirname(__file__))

from map_setup import maze
from measurement import measure
from movement import move

import matplotlib.pyplot as plt


## Simulate starting somewhere with 1 wall, move 2 steps left, then 2 walls...
## Scan 1...
probs = measure(1, None, maze)
probs = move(-1, 0, probs, maze)

plt.matshow(probs)
plt.show()

## Scan 2...
probs = measure(1, probs, maze)
probs = move(-1, 0, probs, maze)
plt.matshow(probs)
plt.show()

## Scan 3...
probs = measure(2, probs, maze)

plt.matshow(probs)
plt.show()
