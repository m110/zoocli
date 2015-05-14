import os
import configparser

from zoocli.exceptions import ConfigNotFound

DEFAULT_CONFIG_PATHS = [
    './zoocli.conf',
    '~/.zoocli.conf',
    '/etc/zoocli/zoocli.conf',
]

config = None


def load_config(path=None):
    global config

    if config:
        return

    config = configparser.ConfigParser()

    paths = DEFAULT_CONFIG_PATHS
    if path:
        paths.insert(0, path)

    for config_path in DEFAULT_CONFIG_PATHS:
        config_path = os.path.expanduser(config_path)
        if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
            config.read(config_path)
            break
    else:
        raise ConfigNotFound("Could not find zoocli.conf")

    return config
