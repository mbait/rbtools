import re
import unittest

from rbtools.api.request import HttpRequest
from rbtools.api.resource import Resource


class StubResource(Resource):
    pass


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
