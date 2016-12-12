import os
from ConfigParser import SafeConfigParser
from ConfigParser import NoOptionError


_MAIN_SECTION = 'main'


# this is exactly how python-decouple handles booleans
# https://github.com/henriquebastos/python-decouple
_BOOL = {'true': True, 'on': True, '1': True,
         'false': False, 'off': False, '0': False}


def cast_bool(obj):
    if obj not in _BOOL:
        raise ValueError('Cannot cast {} to boolean.'.format(obj))
    return _BOOL[obj]


class Loader(object):
    def __init__(self, path):
        self.config_path = path
        self._config = SafeConfigParser()
        self._config.read(self.config_path)

    def config(self, option):
        return self._config.get(_MAIN_SECTION, option)
