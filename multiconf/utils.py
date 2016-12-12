"""
utils.py
~~~~~~~

"""

import sys


PY3 = sys.version_info[0] >= 3

_BOOL = {
    'true': True, 'True': True, '1': True, 'on': True,
    'false': False, 'False': False, '0': False, 'off': False
}


class ConfigurationError(Exception):
    pass


def cast_bool(obj):
    if obj in _BOOL:
        return _BOOL[obj]
    raise ConfigurationError('Cannot cast {} to boolean'.format(obj))


def get_caller_path():
    frame = sys._getframe()
    return frame.f_back.f_back.f_code.co_filename
