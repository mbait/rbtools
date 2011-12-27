"""
Defines API entry point.

This module contains single class providing access for all resources.
Generally, resource methods are named as 'get_' + <resource-name>, e.g.
'get_diff'. In this case the method will block until underlying network
request is sent and the response is received. That is why there is also
asynchronous version for each method, you simply need to add '_async' suffix
to the method name, e.g. 'get_reply_async'. In that case it takes extra
arguments 'on_success' which will be called if data successfully recevied and
optional 'on_failure'.

Example usage:

TODO: place here working example.
"""
from rbtools.api.resource import ResourceFactory


class RBServer(object):
    """Review Board server interface factory.

    """
    _API_SUFFIX = '/api/'
    _ROOT_METHOD_NAME = 'root'
    _TMPL_NAME = 'uri_templates'

    def __init__(self, url, factory=ResourceFactory()):
        self._url = url
        self._factory = factory

    def create(self):
        self._factory.foo(self._ROOT_METHOD_NAME,
                          self._url + self._API_SUFFIX)
        self._load_tmpl_methods()

    def create_async(self):
        pass

    def _load_tmpl_methods(self, root):
        if hasattr(root, self._TMPL_NAME):
            for k, v in getattr(root, self._TMPL_NAME).iteritems():
                #self._factory.foo(k, self._create_tmpl_method(v))
                pass

            delattr(root, self._TMPL_NAME)

    def _create_tmpl_method(self, tmpl, fn):
        return lambda **kwargs: fn(tmpl.format(kwargs))
