"""
Classes, responsible for binding JSON payload with python objects.

See the following document for more info on REST API 2.0:
http://www.reviewboard.org/docs/manual/dev/webapi/
"""
from rbtools.api import errors
from rbtools.api.request import Request, SimpleRequestTransport


ACCEPT_HEADER = 'Accept'

DIFF_MIME_TYPE = 'text/x-patch'

FETCH_METHOD_PREFIX = 'get_'
ASYNC_METHOD_SUFFIX = '_async'

# Special tokens.
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
    """Creates resource objects out of JSON payload.
    """
    EXCLUDE_ATTRIBUTES = [
        METHOD_LIST_TOKEN, RESULT_TOKEN
    ]
    EXCLUDE_METHODS = [
        CREATE_METHOD_TOKEN, UPDATE_METHOD_TOKEN, DELETE_METHOD_TOKEN,
        SELF_METHOD_TOKEN
    ]

    def __init__(self, transport=SimpleRequestTransport()):
        """Initializes factory class.

        Parameters:
            transport - object implementing RequestTransport and responsible
                        for sending requests to the server.
        """
        self.transport = transport

    def create_resource(self, payload, token=None):
        def parse_on_load(token):
            def _parse(payload):
                return self.create_resource(payload, token)

            return _parse

        resource = Resource()
        exclude_attrs = self.EXCLUDE_ATTRIBUTES[:]

        try:
            if token:
                if isinstance(payload[token], list):
                    resource_list = self.create_resource_list(payload[token])
                    resource = ResourceList(resource_list)
                    exclude_attrs.append(token)
                elif isinstance(payload[token], dict):
                    payload = payload[token]
                else:
                    raise errors.InvalidTokenType(token, type(payload[token]))
        except KeyError, e:
            raise errors.TokenNotFound(e)

        if METHOD_LIST_TOKEN in payload:
            links = payload[METHOD_LIST_TOKEN]

            for name in links:
                r = Request(links[name][LINK_HREF_TOKEN],
                            links[name][LINK_METHOD_TOKEN])

                if not name in self.EXCLUDE_METHODS:
                    #self.inject_method(resource, name, r, name)
                    self.inject_method(resource, name, r, parse_on_load(name))
                else:
                    # Handle special methods.
                    if SELF_METHOD_TOKEN == name:
                        self.inject_method(resource, name, r, token)

                    if CREATE_METHOD_TOKEN in links:
                        # TODO: inject 'create'
                        pass

                    if UPDATE_METHOD_TOKEN in links:
                        # TODO: inject 'save'
                        pass

                    if DELETE_METHOD_TOKEN in links:
                        # TODO: inject 'delete'
                        pass

        # Copy all non-special properties into resource.
        for key in payload:
            if not key in exclude_attrs:
                setattr(resource, key, payload[key])

        return resource

    def create_resource_list(self, lst):
        return [self.create_resource(payload) for payload in lst]

    def create_root(self, obj, name, url):
        self.inject_method(obj, name, Request(url))

    def get_method_name(self, name, request, async=False):
        """Contructs method name for injection.

        The result name is mostly based on request parameters.
        """
        method_name = name

        if request.method == 'GET':
            method_name = FETCH_METHOD_PREFIX + method_name

        if async:
            method_name += ASYNC_METHOD_SUFFIX

        return method_name

    def inject_method(self, res, name, request, on_success, on_failure):
        """Generates method requesting resource from the server.

        The result method takes care of both committing network request and
        parsing returned payload (or raising an error if the call was not
        successful).
        """
        setattr(res, self.get_method_name(name, request),
                lambda **kwargs: self.load_resource(request, False,
                                                    on_success, on_failure,
                                                    **kwargs))
        setattr(res, self.get_method_name(name, request, True),
                lambda **kwargs: self.load_resource(request, True,
                                                    on_success, on_failure,
                                                    **kwargs))

    def load_resource(self, request, async=False, on_success=None,
                      on_failure=None, **kwargs):
        request.params.update(kwargs)

        if async:
            return self.transport.send_async(request, on_success, on_failure)
        else:
            try:
                return on_success(self.transport.send(request))
            except errors.RequestError, e:
                if on_failure:
                    on_failure(e)
                else:
                    raise e


class Resource(object):
    """Stub class wrapping response of resource request.

    The class instance tracks assignment of attributes so that if 'save'
    method is avaiable, assigned values will be sent to the server. After
    that their state flushes and if 'save' is called again only changed
    delta will be sent.
    """
    def __init__(self):
        

    def __setattr__(self, name, value):
        super(Resource, self).__setattr__(name, value)


class ResourceList(Resource):
    def __init__(self, lst):
        super(ResourceList, self).__init__()
        self._list = lst

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def all(self, **kwargs):
        cnt = 0
        seq = self.get_self(**kwargs)
        while len(seq):
            for i in iter(seq):
                yield i

            cnt += len(seq)
            seq = self.get_self(start=cnt, **kwargs)

""" Assignment tracker """

class TracksAssignment(object):
    def __init__(self):
        self.acc = {}

    def __delattr__(self, name):
        if name in self.acc:
            del self.acc[name]

        if hasattr(self, name):
            super(TracksAssignment, self).__delattr__(name)

    def __getattribute__(self, name):
        if name in self.acc:
            return self.acc[name]

    def __setattr__(self, name, value):
        if hasattr(self, 'setter'):
            self.setter(name, value)
        else:
            super(TracksAssignment, self).__setattr__(name, value)

    def changed(self):
        return len(self.acc) > 0

    def delta(self):
        delta = self.acc.copy()
        self._unlock()

        for k, v in self.acc.iteritems():
            setattr(self, k, v)

        self.acc.clear()
        self._lock()

        return delta

    def _lock(self):
        def setter(k, v):
            self.acc[k] = v

        self.setter = setter

    def _unlock(self):
        del self.setter


t = TracksAssignment()
t._lock()
print t.changed()
t.a = 1
t.c = 2
t.d = 4
print t.changed()

print t.a
print t.delta()

t.a = 2
print t.a
print t.__dict__
