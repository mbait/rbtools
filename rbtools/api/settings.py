import os

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser


CONFIG_NAME = '.reviewboardrc'
MAIN_OPTION_NAME = 'main'
SEPARATOR = '_'

OPTIONS = [
    (MAIN_OPTION_NAME, 'reviewboard_url'),
    (MAIN_OPTION_NAME, 'user'),
    (MAIN_OPTION_NAME, 'cookie_file'),
    (MAIN_OPTION_NAME, 'api_uri'),
]
ATTRIBUTES = [SEPARATOR.join(opt) for opt in OPTIONS]


class Settings(object):
    """Provides access to user config"""

    def __init__(self):
        self.configs = [
                         os.path.join(p, CONFIG_NAME)
                         for p in [os.path.expanduser('~'), os.getcwd()]
                       ]
        self.config_cache = {}

    def __getattr__(self, name):
        full_name = self._full_name(name)
        if full_name in ATTRIBUTES:
            return self.config_cache[full_name]
        else:
            super(Settings, self).__getattr__(name)

    def __setattr__(self, name, value):
        full_name = self._full_name(name)
        if full_name in ATTRIBUTES:
            self.config_cache[full_name] = value
        else:
            super(Settings, self).__setattr__(name, value)

    def _full_name(self, name):
        """check if the property <name> is valid option"""
        """and prepend main section name if not"""
        if not name in OPTIONS:
            return SEPARATOR.join([MAIN_OPTION_NAME, name])
        else:
            return name

    def load(self):
        """load consequently global options then local ones"""
        # if particular config file was supplied use it
        # else load default files
        cfg = ConfigParser()
        cfg.read(self.configs)
        for opt in OPTIONS:
            (sec, name) = opt
            if cfg.has_section(sec) and cfg.has_option(sec, name):
                self.config_cache[SEPARATOR.join(opt)] = cfg.get(sec, name)

    def save(self, file_name):
        """writes config to file"""
        cfg = ConfigParser()
        for opt in OPTIONS:
            full_name = SEPARATOR.join(opt)
            if full_name in self.config_cache:
                (sec, name) = opt
                if not cfg.has_section(sec):
                    cfg.add_section(sec)
                cfg.set(sec, name, self.config_cache[full_name])

        cfg.write(open(file_name, 'w'))
