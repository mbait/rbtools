from rbtools.api.builder import ResourceBuilder
from rbtools.api.request import HttpRequest
from rbtools.utils.testbase import RBTestBase


class StubTransport(object):
    pass


class HttpRequestTest(RBTestBase):
    def setUp(self):
        self.request = HttpRequest()

    def test_default_values(self):
        self.assertEquals(self.request.get_body(), '')
        self.assertEquals(self.request.get_method(), 'GET')
        self.assertEquals(self.request.get_mime_type(), 'application/json')


class ResourceBuilderTests(RBTestBase):
    def setUp(self):
        self.builder = ResourceBuilder(StubTransport())
