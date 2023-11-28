####################
### BASE MODULES ###
####################
import networkx as _nx
import numpy    as _np
import matplotlib.pyplot as _plt
import sys
import os

######################
### CUSTOM MODULES ###
######################
sys.path.append(os.path.dirname(__file__))

from _maze import OPEN

_=sys.path.pop()

##################
### NODE-GRAPH ###
##################

GRAPH = None

class Directions:
    EAST  = '→'
    WEST  = '←'
    SOUTH = '↓'
    NORTH = '↑'

def _generate_graph():
    global GRAPH
    GRAPH = _nx.Graph()

    for row in range(OPEN.shape[0]):
        for col in range(OPEN.shape[1]):
            if not OPEN[row, col]:
                continue

            GRAPH.add_node((row, col))

            if (row - 1 >= 0) and OPEN[row-1, col]:
                GRAPH.add_edge((row, col), (row-1, col))

            if (col - 1 >= 0) and OPEN[row, col-1]:
                GRAPH.add_edge((row, col), (row, col-1))

    pos = {(i, j): (j, -i) for i in range(OPEN.shape[0]) for j in range(OPEN.shape[1])}

    # _nx.draw(GRAPH, pos, with_labels=True, node_size=700, font_size=8, font_color='white', node_color='skyblue')

    # _plt.draw()

    # _plt.pause(0.001)



def setup() -> None:
    _generate_graph()



def get_shortest_path(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    return _nx.shortest_path(GRAPH, start, end)



def draw(path: list[tuple[int, int]], current_pos: tuple[int, int] = None):
    maze = _np.zeros(OPEN.shape)
    for i, idx in enumerate(path):
        maze[*idx] = 1 if (i != 0 and i != len(path)-1) else 0.5
    if current_pos:
        maze[current_pos] = 1.5
    _plt.close()
    _plt.matshow(maze)
    _plt.draw()
    _plt.pause(0.001)



def close_plt():
    _plt.close()



############
### TEST ###
############
if __name__ == '__main__':
    _generate_graph()

    path = get_shortest_path((0, 0), (3, 7))

    draw(path, (1, 3))

    input("[ENTER] to exit...")

