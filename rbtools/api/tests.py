from rbtools.api.builder import ResourceBuilder
from rbtools.api.request import HttpRequest
from rbtools.api.resource import Resource
from rbtools.utils.testbase import RBTestBase


class MockTransport(object):
    def __init__(self):
        self._resources = {}

    def add_resource(self, uri, resource):
        self._resources[uri] = resource

    def send_request(self, request, callback):
        pass


class StubResource(Resource):
    pass


class HttpRequestTests(RBTestBase):
    def test_default_values(self):
        request = HttpRequest('/')
        self.assertEquals(request.get_url(), '/')
        self.assertEquals(request.get_method(), 'GET')
        self.assertEquals(request.get_body(), '')

    def test_custom_method(self):
        request = HttpRequest('/', 'POST')
        self.assertEquals(request.get_method(), 'POST')


class ResourceBuilderTests(RBTestBase):
    def setUp(self):
        transport = MockTransport()
        transport.add_resource('/foos/1/',  {'prop': 'x'})
        transport.add_resource('/foos/2/',  {'prop': 'y'})
        transport.add_resource('/foos/3/',  {'prop': 'z'})
        transport.add_resource('/bars/1/',  {'field': 'foo'})
        transport.add_resource('/bars/2/',  {'field': 'bar'})
        transport.add_resource('/bars/3/',  {'field': 'baz'})
        transport.add_resource('/foos/1/bazes/1/',  {'attr': '101'})
        transport.add_resource('/foos/2/bazes/2/',  {'attr': '102'})
        transport.add_resource('/foos/3/bazes/3/',  {'attr': '103'})
        transport.add_resource('/foos/3/bazes/3/quxes/1/',  {'value': 'name'})

        transport.add_resource('/reqs/1/', {'author': 'user1', 'group': 'dev'})
        transport.add_resource('/reqs/2/', {'author': 'user2', 'group': 'gfx'})
        transport.add_resource('/reqs/3/', {'author': 'user3', 'group': 'sfx'})
        transport.add_resource('/reqs/1/revs/', {'file': 'main.cpp'})
        transport.add_resource('/reqs/2/revs/', {'file': 'layout.svg'})
        transport.add_resource('/reqs/3/revs/', {'file': 'ambient.wav'})

        self.builder = ResourceBuilder(transport)

    def test_build_generic_resource(self):
        resource = self.builder.build(Resource, {'stat': 'ok'})
        self.assertIsInstance(resource, Resource)

    def test_build_custom_resource(self):
        resource = self.builder.build(StubResource, {'stat': 'ok'})
        self.assertIsInstance(resource, StubResource)

    def test_build_resource_with_token(self):
        resource = self.builder.build(Resource, {'tok': {}, 'stat': 'ok'},
                                      token='tok')
        self.assertIsInstance(resource, Resource)
