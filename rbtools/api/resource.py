"""
Classes, responsible for binding JSON payload with python objects.

See the following document for more info on REST API 2.0:
http://www.reviewboard.org/docs/manual/dev/webapi/
"""
try:
    from json import loads as json_loads
except ImportError:
    from simplejson import loads as json_loads

from rbtools.api import error, FETCH_REQUEST_METHOD
from rbtools.api.request import Request, ThreadedRequestTransport


ACCEPT_HEADER = 'Accept'

DIFF_MIME_TYPE = 'text/x-patch'

FETCH_METHOD_PREFIX = 'get_'
ASYNC_METHOD_SUFFIX = '_async'

METHOD_LIST_TOKEN = 'links'
RESULT_TOKEN = 'stat'
LINK_HREF_TOKEN = 'href'
LINK_METHOD_TOKEN = 'method'
# CRUD.
CREATE_METHOD_TOKEN = 'create'
UPDATE_METHOD_TOKEN = 'update'
DELETE_METHOD_TOKEN = 'delete'
# Resource navigation.
PREV_METHOD_TOKEN = 'prev'
SELF_METHOD_TOKEN = 'self'
NEXT_METHOD_TOKEN = 'next'


class ResourceFactory(object):
    EXCLUDE_ATTRIBUTES = [
        METHOD_LIST_TOKEN, RESULT_TOKEN
    ]
    EXCLUDE_METHODS = [
        CREATE_METHOD_TOKEN, UPDATE_METHOD_TOKEN, DELETE_METHOD_TOKEN
    ]

    def __init__(self, transport=ThreadedRequestTransport()):
        self.transport = transport

    def create_method(self, resource, name, request, has_token=None):
        def fetch(*args, **kwargs):
            try:
                payload = json_loads(self.transport.send(request))
            except TypeError, e:
                raise error.InvalidPayload(e)

            token = None
            if has_token:
                token = name

            return self.create_resource(payload, token)

        def fetch_async(on_success, on_failure=None, *args, **kwargs):
            self.transport.send_async(request, on_success, on_failure)

        setattr(resource, self.get_method_name(name, request), fetch)

    def create_resource(self, payload, token=None):
        resource = Resource()

        if token:
            if not token in payload:
                raise error.TokenNotFound(token)

            if isinstance(payload[token], list):
                resource = ResourceList(
                        self.create_resource_list(payload[token]))
                del payload[token]
            elif isinstance(payload[token], dict):
                payload = payload[token]
            else:
                raise error.InvalidTokenType(token, type(payload[token]))

        if METHOD_LIST_TOKEN in payload:
            links = payload[METHOD_LIST_TOKEN]
            for name in links:
                r = Request(links[name][LINK_HREF_TOKEN])

                self.create_method(resource, name, r,
                                   SELF_METHOD_TOKEN != name)

        # Copy all non-special properties into resource.
        for key in payload:
            if not key in self.EXCLUDE_ATTRIBUTES:
                setattr(resource, key, payload[key])

        return resource

    def create_resource_list(self, lst):
        return [self.create_resource(payload) for payload in lst]

    def get_method_name(self, name, request, async=False):
        method_name = name

        if FETCH_REQUEST_METHOD == request.method:
            method_name = FETCH_METHOD_PREFIX + method_name

        if async:
            method_name += ASYNC_METHOD_SUFFIX

        return method_name


class Resource(object):
    """Stub class wrapping response of resource request.

    Concrete resource implementations should derive from this class.
    """
    pass


class ResourceList(Resource):
    def __init__(self, lst):
        super(ResourceList, self).__init__()
        self._iter = iter(lst)

    def __iter__(self):
        return self._iter

    def all(self, *args, **kwargs):
        method = FETCH_METHOD_PREFIX + SELF_METHOD_TOKEN
        return getattr(self, method)(*args, **kwargs)

    def all_async(self, on_success):
        pass


class DiffResource(Resource):
    """Implements 'diff' resource."""
    def _diff_request(self):
        # TODO: Deep copy required here.
        request = self._links[SELF_METHOD_TOKEN]
        request.set_header(ACCEPT_HEADER, DIFF_MIME_TYPE)

    def get_diff(self):
        return self.send_request(self._diff_request())

    def get_diff_async(self, on_success):
        self.send_request_async(self._diff_request())


class ReviewRequestResource(Resource):
    """Implements 'review_request' resource."""
    pass
