try:
    from json import loads as json_loads
except ImportError:
    from simplejson import loads as json_loads

from rbtools.api.request import Request, RequestTransport
from rbtools.api.resource import Resource, ResourceFactory
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
        self.factory = ResourceFactory(MockRequestTransport())

    def test_inject_method_simple(self):
        """Duck test of method generation."""
        res = Resource()
        self.factory.inject_method(res, 'foo', Request(''))
        self.factory.inject_method(res, 'bar', Request('', 'POST'))

        # 'GET' requests are always prepended with 'get_'.
        self.assertTrue(callable(res.get_foo))
        self.assertTrue(callable(res.get_foo_async))

        self.assertTrue(callable(res.bar))
        self.assertTrue(callable(res.bar_async))

    def test_parse_attributes(self):
        """Test parsing resource attributes."""
        payload = json_loads('{"foo":"bar", "bar":"baz"}')
        res = self.factory.create_resource(payload)

        self.assertEqual(res.foo, 'bar')
        self.assertEqual(res.bar, 'baz')

    def test_parse_attributes_with_token(self):
        """Test parsing of payload attributes with token provided."""
        payload = json_loads('{"foo_token":{"foo":"bar", "bar":"baz"}}')
        res = self.factory.create_resource(payload, 'foo_token')

        self.assertEqual(res.foo, 'bar')
        self.assertEqual(res.bar, 'baz')

    def test_parse_methods(self):
        """Test parsing resource methods."""
        payload = json_loads('{"links":{"foo":{"href":"bar","method":"GET"},'
                             '"bar":{"href":"foo","method":"POST"}}}')
        res = self.factory.create_resource(payload)

        self.assertTrue(callable(res.get_foo))
        self.assertTrue(callable(res.get_foo_async))
        self.assertTrue(callable(res.bar))
        self.assertTrue(callable(res.bar_async))

    def test_parse_methods_with_token(self):
        """Test parsing resource methods with token provided."""
        payload = json_loads('{"foo_token":{"links":{"foo":{"href":"bar","meth'
                             'od":"GET"},"bar":{"href":"foo","method":"POST"}}'
                             '}}')
        res = self.factory.create_resource(payload, 'foo_token')

        print res.__dict__
        self.assertTrue(callable(res.get_foo))
        self.assertTrue(callable(res.get_foo_async))
        self.assertTrue(callable(res.bar))
        self.assertTrue(callable(res.bar_async))

    def test_parse_resource_list(self):
        """Test parsing of resource list."""
        payload = json_loads('{"foo_list":[{"foo":"bar","links":{"get":{"href"'
                             ':"spam","method":"GET"},"post":{"href":"eggs","m'
                             'ethod":"POST"}}},{"bar":"baz","links":{"fetch":{'
                             '"href":"spam2","method":"GET"},"send":{"href":"e'
                             'ggs2","method":"POST"}}}],"links":{"fooo":{"href'
                             '":"foo","method":"UPDATE"},"baar":{"method":"DEL'
                             'ETE","href":"bar"}},"baaz":"quux"}')
        res_list = self.factory.create_resource(payload, 'foo_list')

        for item in res_list:
            self.assertTrue(isinstance(item, Resource))

        i = iter(res_list)
        item = i.next()
        self.assertEqual(item.foo, 'bar')
        self.assertTrue(callable(item.get_get))
        self.assertTrue(callable(item.post))
        item = i.next()
        self.assertEqual(item.bar, 'baz')
        self.assertTrue(callable(item.get_fetch))
        self.assertTrue(callable(item.send))

    def test_call_method(self):
        """Test method invocation of generated resource."""
        payload = json_loads('{"links":{"foo":{"method":"GET","href":"foo"}}}')
        res = self.factory.create_resource(payload)
        foo = res.get_foo()

        self.assertEqual(foo.bar, 'baz')

    def test_get_root(self):
        """Test injection of root accessor."""
        res = Resource()
        self.factory.create_root(res, 'root', 'root')
        self.assertTrue(callable(res.get_root))
        self.assertTrue(callable(res.get_root_async))

        root = res.get_root()
        self.assertEqual(root.result, 42)

    def test_resource_list_iterator(self):
        """Test resource list iterator."""
        json = '{"links":{"bar":{"method":"GET","href":"bar"}}}'
        res = self.factory.create_resource(json_loads(json))
        for item in res.get_bar():
            self.assertTrue(isinstance(item, Resource))
            self.assertTrue(item.foo == 'bar' or item.foo == 'baz')

    def test_resource_list_all_iterator(self):
        json = '{"links":{"bar":{"method":"GET","href":"bar"}}}'
        res = self.factory.create_resource(json_loads(json))
        bar = res.get_bar()

        # TODO: check all()
        self.assertTrue(bar)

    def test_create_resource(self):
        """Tests 'create' method of a resource list."""
        # TODO: test 'create' method.
        pass

    def test_update_resource(self):
        """Tests 'update' method of a resource lists"""
        # TODO: test 'save' method
        pass

    def test_self_request(self):
        """Tests 'self' method of a resource."""
        json = '{"foo":{"links":{"self":{"method":"GET","href":"foo"}}}}'
        res = self.factory.create_resource(json_loads(json), 'foo')

        res = res.get_self()
        self.assertEqual(res.bar, 'baz')
