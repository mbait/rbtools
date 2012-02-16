import getpass


class AuthReader(object):
    """Generic interface for requesting authentication data."""
    def get_auth_data(self, realm, uri):
        raise NotImplementedError


class TerminalAuthReader(AuthReader):
    """Requests authentication data via terminal prompts."""
    def get_auth_data(self, realm, uri):
        print "Enter username and password for %s at %s" % (realm, uri)
        return raw_input('User: '), getpass.getpass('Password: ')
