from rbtools.api.builder import ResourceBuilder
from rbtools.api.request import HttpRequest
from rbtools.api.resource import Resource
from rbtools.utils.testbase import RBTestBase


class MockTransport(object):
    def __init__(self, url):
        self._url = url


class StubResource(Resource):
    pass


class HttpRequestTests(RBTestBase):
    def setUp(self):
        self.request = HttpRequest()

    def test_default_values(self):
        self.assertEquals(self.request.get_body(), '')
        self.assertEquals(self.request.get_method(), 'GET')


class ResourceBuilderTests(RBTestBase):
    def setUp(self):
        self.builder = ResourceBuilder(MockTransport('local'))

    def test_build_generic_resource(self):
        resource = self.builder.build(Resource, {'stat': 'ok'})
        self.assertIsInstance(resource, Resource)

    def test_build_custom_resource(self):
        resource = self.builder.build(StubResource, {'stat': 'ok'})
        self.assertIsInstance(resource, StubResource)
