try:
    from json import loads as json_loads
except ImportError:
    from simplejson import loads as json_loads

from rbtools.api.errors import get_exception_by_code, RequestError
from rbtools.api.request import RequestTransport
from rbtools.utils.testbase import RBTestBase


class MockRequestTransport(RequestTransport):
    payloads = {
        'foo': '{"foo":{"bar":"baz"}}',
        'bar': '{"bar":[{"foo":"bar","foo":"baz"}]}',
        'baz': '',
        'qux': '',
        'root': '{"result":42}'
    }

    def send(self, request):
        return json_loads(self.payloads[request.url])


class ResourceFactoryTest(RBTestBase):
    def setUp(self):
        super(ResourceFactoryTest, self).setUp()


class ErrorsTests(RBTestBase):
    def _is_valid_exception(self, cls, code):
        self.assert_(issubclass(cls, RequestError))
        self.assert_(cls.code == code)

    def test_unknown_error(self):
        """Test retrieving exception for unknown request errors."""
        self._is_valid_exception(get_exception_by_code(-1), -1)

    def test_known_errors(self):
        """Test retrieving exception for some known request errors."""
        for code in [101, 203, 218]:
            self._is_valid_exception(get_exception_by_code(code), code)
