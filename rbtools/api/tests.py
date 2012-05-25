import re
import unittest

from rbtools.api.client import RBClient
from rbtools.api.builder import ResourceBuilder
from rbtools.api.request import HttpRequest
from rbtools.api.resource import Resource
from rbtools.api.transport import Transport, UrllibTransport


class StubTransport(Transport):
    def __init__(self, *args):
        super(StubTransport, self).__init__(args)

    def __call__(self, **kwargs):
        pl = self._get_resource(self._request.get_url())

        return self._builder.build(pl, self.__class__)


class ResourceTests(unittest.TestCase):
    pass


class ResourceBuilderTests(unittest.TestCase):
    def setUp(self):
        self.res = Resource()
        self.builder = ResourceBuilder()

    def test_build_resource(self):
        self.builder.build(self.res, {'foo': 'bar', 'id': 1, 'links': [],
                                      'stat': 'ok'})
        self.assertFalse(hasattr(self.res, 'stat'))
        self.assertEquals(self.res.foo, 'bar')
        self.assertEquals(self.res.id, 1)

    def test_build_resource_with_token(self):
        payload = {'tok': {'baz': 'qux', 'count': 42, 'links': []}}
        self.builder.build(self.res, payload, 'tok')
        self.assertEquals(self.res.baz, 'qux')
        self.assertEquals(self.res.count, 42)

    def test_build_resource_list(self):
        payload = {'list': [{}, {}], 'count': 'many', 'code': 200, 'links': []}
        self.builder.build(self.res, payload, 'list')
        self.assertEquals(self.res.count, 'many')
        self.assertEquals(self.res.code, 200)


class HttpRequestTests(unittest.TestCase):
    def setUp(self):
        self.request = HttpRequest('/')

    def test_default_values(self):
        self.assertEquals(self.request.get_url(), '/')
        self.assertEquals(self.request.get_method(), 'GET')
        self.assertIsNone(self.request.get_body())

    def test_custom_method(self):
        self.request.set_method('PUT')
        self.assertEquals(self.request.get_method(), 'PUT')

        request = HttpRequest('/', 'POST')
        self.assertEquals(request.get_method(), 'POST')

    def test_post_form_data(self):
        request = HttpRequest('/', 'POST')
        request.add_field('foo', 'bar')
        request.add_field('bar', 42)
        request.add_field('err', 'must-be-deleted')
        request.add_field('name', 'somestring')
        request.del_field('err')

        ctype, content = request.get_body()
        m = re.match('^multipart/form-data; boundary=(.*)$', ctype)
        self.assertIsNotNone(m)
        fields = [l.strip() for l in content.split('--' + m.group(1))][1:-1]

        d = {}

        for f in fields:
            lst = f.split('\r\n\r\n')
            self.assertEquals(len(lst), 2)
            k, v = lst

            m = re.match('Content-Disposition: form-data; name="(.*?)"$', k)
            self.assertIsNotNone(m)
            d[m.group(1)] = v

        self.assertEquals(d, {'foo': 'bar', 'bar': '42', 'name': 'somestring'})

    def test_post_form_files(self):
        pass


class RBClientTests(unittest.TestCase):
    def test_root_is_a_transport(self):
        self.assertIsInstance(RBClient('').get_root, Transport)
        self.assertIsInstance(RBClient('', UrllibTransport).get_root,
                                       UrllibTransport)

# vim: set sw=4 :
# vim: set ts=4 :
# vim: set expandtab :
