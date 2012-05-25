import re

from rbtools.api.request import HttpRequst
from rbtools.api.builder import ResourceBuilder
from rbtools.api.transport import UrllibTransport


class RBClient(object):
    """ Entry point for accessing RB resources through the web API.
    """
    def __init__(self, url, transport_cls=UrllibTransport):
            self.get_root = transport_cls(Link(ResourceBuilder(), HttpRequst(url)))

# vim: set ts=4 :
# vim: set sw=4 :
# vim: set expandtab :
