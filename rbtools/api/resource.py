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
SELF_METHOD_TOKEN = 'self'


class MethodInjector(object):
    def __init__(self, factory):
        self.factory = factory

    def set_request(self, request):
        self.request = request

    def set_success_callback(self, on_success):
        self.on_success = on_success

    def set_failure_callback(self, on_failure):
        self.on_failure = on_failure

    def inject(self, name, resource):
        """Generates methods requesting resource from the server.

        There are two methods generated: blocked and asynchronous. The first
        method is blocked until the data received or an error occured, and the
        second one returns These
        methods take care of both committing network request and parsing
        returned payload (or raising an error if the call was not successful).
        """
        setattr(resource, self._get_method_name(name),
                MethodInjector._create_sync_callback(self.transport,
                                                     self.request,
                                                     self.on_success,
                                                     self.on_failure))
        setattr(resource, self._get_method_name(name, async=True),
                MethodInjector._create_async_callback(self.transport,
                                                      self.request,
                                                      self.on_success,
                                                      self.on_failure))

    def _get_method_name(self, name, async):
        """Contructs method name for injection.

        The result name is mostly based on request parameters.
        """
        if self.request.method == 'GET':
            name = FETCH_METHOD_PREFIX + name

        if async:
            name += ASYNC_METHOD_SUFFIX

        return name

    @staticmethod
    def _create_sync_callback(transport, request, on_success, on_failure):
        def sync_callback(**kwargs):
            # TODO: catch low-level network exceptions
            return on_success(transport.send(request))

        return sync_callback

    @staticmethod
    def _create_async_callback(transport, request, on_success, on_failure):
        def async_callback(**kwargs):
            transport.send_async(request, on_success, on_failure)

        return async_callback


class ResourceBuilder(object):
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
            transport - as object implementing RequestTransport and responsible
                        for sending requests to the server.
        """
        self.transport = transport

    def create_resource(self, payload, token=None):
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

            injector = MethodInjector(self.transport)

            for name in links:
                injector.set_request(Request(links[name][LINK_HREF_TOKEN],
                                             links[name][LINK_METHOD_TOKEN]))

                if not name in self.EXCLUDE_METHODS:
                    on_success = lambda p: self.create_resource(p, name)
                    injector.set_success_callback(on_success)
                    injector.inject(resource, name)
                else:
                    # Handle special methods.
                    if SELF_METHOD_TOKEN == name:
                        on_success = lambda p: self.create_resource(p, token)
                        injector.set_success_callback(on_success)
                        injector.inject(resource, name)

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
        #self.inject_method(obj, name, Request(url))
        injector = MethodInjector(self.transport)
        injector.set_success_callback(self.create_resource)
        injector.inject(obj, name, url)


class Resource(object):
    """Stub class wrapping response of resource request.

    The class instance tracks assignment of attributes so that if 'save'
    method is avaiable, assigned values will be sent to the server. After
    that their state flushes and if 'save' is called again only changed
    delta will be sent.
    """
    def __init__(self):
        self.acc = {}

    def __delattr__(self, name):
        if name in self.acc:
            del self.acc[name]

        if hasattr(self, name):
            super(Resource, self).__delattr__(name)

    def __getattribute__(self, name):
        if name in self.acc:
            return self.acc[name]

    def __setattr__(self, name, value):
        if hasattr(self, 'setter'):
            self.setter(name, value)
        else:
            super(Resource, self).__setattr__(name, value)

    def is_changed(self):
        return len(self.acc) > 0

    def get_delta(self):
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
