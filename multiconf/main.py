import os
import re
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
_LEGAL_CASTS = (int, float)

INTERP_RE = re.compile(r'\${(.*?)}')


class Config(object):

    def __init__(self, path):
        self.parser = ConfigParser()
        _read = self.parser.read(path)
        if not _read:
            raise ConfigurationError(
                'Could not find config file for {}'.format(path)
            )
        self.schemes_list = self.parser.sections()
        self.scheme = self.parser.get(_MAIN_SECTION, 'scheme')
        if self.scheme not in self.schemes_list:
            raise ConfigurationError(
                '{} is declared as a scheme but is '
                'not a section in the configuration'
                .format(self.scheme)
            )

    def trim(self, s):
        return INTERP_RE.sub(r'{\1}', s)

    def __call__(self, option, section=None, cast=None):
        value, section = self._resolve(option, section)
        if INTERP_RE.search(value):
            value = self._interpolate(value, section)
        return self._cast(value, cast)

    def _resolve(self, option, section=None):
        if section is not None:
            return self.parser.get(section, option), section
        if option.lower() in self.parser.options(self.scheme):
            return self.parser.get(self.scheme, option), self.scheme
        if option.lower() in self.parser.options(_MAIN_SECTION):
            return self.parser.get(_MAIN_SECTION, option), _MAIN_SECTION
        raise ConfigurationError(
            'Option {} was not found in scheme "{}" section nor in "main"'
            .format(option, self.scheme)
        )

    def _interpolate(self, value, section):
        # import ipdb; ipdb.set_trace()
        repl_opts = INTERP_RE.findall(value)
        if section != _MAIN_SECTION:
            section = None
        repl_opts = {opt: self(opt, section) for opt in repl_opts}
        template = self.trim(value)
        return template.format(**repl_opts)

    def _cast(self, value, dest):
        try:
            if dest is None:
                return value
            if dest is bool:
                return cast_bool(value)
            if dest in _LEGAL_CASTS:
                return dest(value)
        except ValueError:
            raise ConfigurationError(
                'Cannot cast {} to {}'.format(value, dest)
            )
        raise ConfigurationError(
            '{} is not a valid cast function. Legal casts are: {}'
            .format(', '.join(_LEGAL_CASTS + ['bool']))
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
