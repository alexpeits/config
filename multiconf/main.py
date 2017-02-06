import os
from configparser import (
    ConfigParser, ExtendedInterpolation, NoOptionError
)

from .utils import (
    cast_bool, ConfigurationError
)


_MAIN = 'main'
_SCHEME_OPT = 'scheme'
_LEGAL_CASTS = (int, float)


class Config(object):

    def __init__(self, conf, main=_MAIN, scheme_opt=_SCHEME_OPT):
        self.parser = ConfigParser(interpolation=ExtendedInterpolation())
        self.parser.read_string(conf)
        self._schemes_list = self.parser.sections()
        self.scheme = self.parser.get(main, scheme_opt)
        if self.scheme not in self._schemes_list:
            raise ConfigurationError(
                '"{}" is declared as a scheme but is '
                'not a section in the configuration'
                .format(self.scheme)
            )
        self._main = main
        self._scheme_opt = scheme_opt

    @classmethod
    def from_path(cls, path, main=_MAIN, scheme_opt=_SCHEME_OPT):
        if not (os.path.exists(path) and os.path.isfile(path)):
            raise ConfigurationError('{} is not a file'.format(path))
        with open(path) as f:
            data = f.read()
        return cls(data, main, scheme_opt)

    @classmethod
    def from_file(cls, fobj, main=_MAIN, scheme_opt=_SCHEME_OPT):
        data = fobj.read()
        return cls(data, main, scheme_opt)

    def __call__(self, option, section=None, cast=None):
        value = self._resolve(option, section)
        return self._cast(value, cast)

    def _resolve(self, option, section=None):
        if section is not None:
            try:
                return self.parser.get(section, option)
            except NoOptionError:
                raise ConfigurationError(
                    'Option "{}" was not found in section "{}"'
                    .format(option, section)
                )
        if option.lower() in self.parser.options(self.scheme):
            return self.parser.get(self.scheme, option)
        if option.lower() in self.parser.options(self._main):
            return self.parser.get(self._main, option)
        raise ConfigurationError(
            'Option "{}" was not found in scheme "{}" section '
            'nor in the main section'
            .format(option, self.scheme)
        )

    def _cast(self, value, dest):
        if dest is None:
            return value
        try:
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
