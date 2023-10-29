import os, yaml

def get_config():
    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as cfg_file:
        cfg = yaml.safe_load(cfg_file)
    return cfg
