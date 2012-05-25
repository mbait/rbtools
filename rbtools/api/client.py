import re

from rbtools.api.request import HttpRequest
from rbtools.api.builder import ResourceBuilder
from rbtools.api.transport import UrllibTransport


class RBClient(object):
    """ Entry point for accessing RB resources through the web API.
    """
    def __init__(self, url, transport_cls=UrllibTransport):
        self._root = transport_cls((ResourceBuilder(), HttpRequest(url + '/api')))

    @property
    def get_root(self):
        return self._root

# vim: set ts=4 :
# vim: set sw=4 :
# vim: set expandtab :
