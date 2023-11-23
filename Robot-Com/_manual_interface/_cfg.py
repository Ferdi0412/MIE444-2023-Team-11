import os as _os, yaml as _yaml

with open(_os.path.join(_os.path.dirname(__file__), 'robot.yaml'), 'r') as cfg_file:
    _cfg: dict = _yaml.safe_load(cfg_file)
