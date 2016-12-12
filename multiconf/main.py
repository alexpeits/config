import os
from glob import glob
from ConfigParser import NoOptionError

from .utils import (
    PY3, cast_bool,
    ConfigurationError
)

if PY3:
    from ConfigParser import ConfigParser
else:
    from ConfigParser import SafeConfigParser as ConfigParser


_MAIN_SECTION = 'main'
_SCHEME_OPTION = 'scheme'


class Config(object):

    def __init__(self, path):
        self.parser = ConfigParser()
        _read = self.parser.read(path)
        if not _read:
            raise ConfigurationError(
                'Could not find config file for {}'.format(path)
            )


class AutoConfig(Config):

    _default_filenames = ('.env', 'config.ini', 'conf.ini')

    def __init__(self, filenames=()):
        def_filenames = list(self._default_filenames)
        def_filenames.extend(filenames)
        config_path = self._get_config(def_filenames)
        super(AutoConfig, self).__init__(config_path)

    def _get_config(self, filenames):
        parent = os.path.abspath(os.curdir)
        for fn in filenames:
            path = os.path.join(parent, fn)
            if os.path.exists(path):
                return path
        raise ConfigurationError('No config file was found')
