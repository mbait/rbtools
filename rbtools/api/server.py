"""
Defines API entry point.

This module contains single class providing access for all resources.
Generally, resource methods are named as 'get_' + <resource_name>, e.g.
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
    """Review Board server interface."""
    _API_SUFFIX = '/api/'
    _ROOT_METHOD_NAME = 'root'

    def __init__(self, url, factory=ResourceFactory()):
        factory.create_root(self, self._ROOT_METHOD_NAME,
                            url + self._API_SUFFIX)
