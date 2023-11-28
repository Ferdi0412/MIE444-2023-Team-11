###############
### MODULES ###
###############
import os   as _os
import yaml as _yaml



#########################
### ROBOT CONFIG FILE ###
#########################
def get_robot_config() -> dict:
    with open(_os.path.join(_os.path.dirname(__file__), 'robot.yaml'), 'r') as cfg_file:
        _robot_cfg: dict = _yaml.safe_load(cfg_file)
    return _robot_cfg




##########################
### GEN. SCREEN CONFIG ###
##########################
SCREEN_WIDTH  = 1200
SCREEN_HEIGHT = 800

PIXEL_SCALE   = 20 ## This means that 8 pixels represents 1 inch...

X0 = SCREEN_WIDTH // 2
Y0 = SCREEN_HEIGHT // 2



##########################
### GEN. COLOUR CONFIG ###
##########################
NEUTRAL_BG = [50, 50, 50]
ROBOT_FILL = [200, 140, 80]
BLACK      = [0,   0,   0  ]
WHITE      = [255, 255, 255]

GREEN      = [20,  20,  180]
ORANGE     = [220, 80,  0]

RAY_COL     = GREEN
RAY_AVG_COL = ORANGE
