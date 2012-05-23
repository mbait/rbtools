import re

import rbtools.api.resource as res
from rbtools.api.builder import ResourceBuilder


class RBClient(object):
    """ Entry point for accessing RB resources through the web API.
    """
    DEFAULT_BINDINGS = {
        '/': res.RootResource,
        '/review-requests/*/diffs/': res.DiffListResource,
        '/review-requests/*/diffs/*/': res.DiffResource,
    }

    def __init__(self, url_prefix, bindings={}):
        reg = {}

        for b in [self.DEFAULT_BINDINGS, bindings]:
            for pat, cls in b.iteritems():
                reg[re.compile(pat.replace('*', '\w+'))] = cls

        self._builder = ResourceBuilder(reg)

    def get_root(self, callback=lambda: None):
        Foo(self._builder).fetch('/', callback)
        #callback(
        #callback(self._builder.build('/'))
