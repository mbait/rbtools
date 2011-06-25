import os

from ConfigParser import ConfigParser


CONFIG_NAME = '.reviewboardrc'
MAIN_SECTION_NAME = 'main'
SEPARATOR = '_'

OPTIONS = [
    (MAIN_SECTION_NAME, 'reviewboard_url'),
    (MAIN_SECTION_NAME, 'user'),
    (MAIN_SECTION_NAME, 'cookie_file'),
    (MAIN_SECTION_NAME, 'api_uri'),
]
ATTRIBUTES = [SEPARATOR.join(opt) for opt in OPTIONS]


class Settings(object):
    """Provides access to user config"""

    def __init__(self):
        self.configs = [os.path.join(p, CONFIG_NAME)
                        for p in [os.path.expanduser('~'), os.getcwd()]]
        self.options = {}

    def __getattr__(self, name):
        full_name = self._full_name(name)
        if full_name in ATTRIBUTES:
            return self.options[full_name]
        else:
            raise AttributeError, "'%s' is neither attribute nor option name" \
                                  % name

    def __setattr__(self, name, value):
        full_name = self._full_name(name)
        if full_name in ATTRIBUTES:
            self.options[full_name] = value
        else:
            object.__setattr__(self, name, value)

    def _full_name(self, name):
        """check if the property <name> is valid option"""
        """and prepend MAIN_SECTION_NAME if not"""
        if not name in OPTIONS:
            return SEPARATOR.join([MAIN_SECTION_NAME, name])
        else:
            return name

    def load(self):
        """load consequently global options then local ones"""
        # if particular config file was supplied use it
        # else load default files
        cfg = ConfigParser()
        cfg.read(self.configs)
        for sec, name in OPTIONS:
            if cfg.has_section(sec) and cfg.has_option(sec, name):
                self.options[SEPARATOR.join([sec, name])] = cfg.get(sec, name)

    def save(self, file_name):
        """writes config to file"""
        cfg = ConfigParser()
        for opt in OPTIONS:
            full_name = SEPARATOR.join(opt)
            if full_name in self.options:
                (sec, name) = opt
                if not cfg.has_section(sec):
                    cfg.add_section(sec)
                cfg.set(sec, name, self.options[full_name])

        cfg.write(open(file_name, 'w'))

    def save_local(self):
        self.save(os.path.join(os.getcwd(), CONFIG_NAME))

    def save_global(self):
        self.save(os.path.join(os.path.expanduser('~'), CONFIG_NAME))
