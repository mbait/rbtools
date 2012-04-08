import simplejson
import unittest

from rbtools.api.builder import ResourceBuilder
from rbtools.api.request import HttpRequest
from rbtools.api.resource import Resource


class StubResource(Resource):
    pass


class MockTransport(object):
    def __init__(self):
        self._resources = {}

    def _create_payload(self, path):
        return {}

    def get_payload(self, path):
        payload = {'stat': 'ok'}
        resource = payload

        names = [name for name in path.split('/') if name]
        children = [res for res in self._resources if res.startswith(path)]

        if names:
            res_name = names[-2][:-1]
            resource[res_name] = {'id': names[-1]}
            resource = resource[res_name]
            # Set previously saved properties.
            resource.update(self._resources[path])
        else:
            # Construct uri_templates
            resource['uri_templates'] = {'root': '/'}

        # Fill links.
        links = {
            ResourceBuilder.SELF_TOK: {
                'method': 'GET',
                'href': path
            }
        }

        for child in children:
            names = [r for r in child.split('/') if r]
            child_name = names[-2]
            links[child_name] = {'method': 'GET',
                                 'href': path + child_name + '/'}

        resource[ResourceBuilder.LINKS_TOK] = links

        return payload

    def set_resource(self, path, resource):
        self._resources[path] = resource

    def send_request(self, request, callback):
        if request.get_method() == 'GET':
            pl = self._create_payload(request.get_url())
            callback(simplejson.dumps(pl))
        else:
            pass


class MockTransportTests(unittest.TestCase):
    def setUp(self):
        self._transport = MockTransport()

    def assertInAndEquals(self, key, value, dct):
        self.assertIn(key, dct)
        self.assertEquals(dct[key], value)

    def assertIsRootResource(self, payload):
        self.assertInAndEquals('stat', 'ok', payload)
        self.assertIn(ResourceBuilder.LINKS_TOK, payload)
        links = payload[ResourceBuilder.LINKS_TOK]
        self.assertIn(ResourceBuilder.SELF_TOK, links)
        self.assertInAndEquals('href', '/', links[ResourceBuilder.SELF_TOK])
        self.assertInAndEquals('method', 'GET',
                               links[ResourceBuilder.SELF_TOK])

        self.assertIn('uri_templates', payload)
        self.assertInAndEquals('root', '/', payload['uri_templates'])

    def assertIsChildResource(self, payload, name):
        self.assertInAndEquals('stat', 'ok', payload)
        self.assertIn(name, payload)
        self.assertIsInstance(payload[name], dict) 

    def test_create_root_resource(self):
        self.assertIsRootResource(self._transport.get_payload('/'))

    def test_create_non_root_resource(self):
        self._transport.set_resource('/foos/42/', {'attr': 'name'})
        payload = self._transport.get_payload('/foos/42/')
        self.assertIsChildResource(payload, 'foo')

        foo = payload['foo']
        self.assertInAndEquals('id', '42', foo)
        self.assertInAndEquals('attr', 'name', foo)

    def test_create_links_for_child_resources(self):
        self._transport.set_resource('/foos/42/', {'attr': 'name'})
        self._transport.set_resource('/foos/42/bars/1', {'prop': 'email'})
        self._transport.set_resource('/foos/42/bazes/2', {'prop': 'email'})

        payload = self._transport.get_payload('/foos/42/')
        self.assertIsChildResource(payload, 'foo')

        foo = payload['foo']
        self.assertIn('bars', foo['links'])
        self.assertEquals(foo['links']['bars']['href'], '/foos/42/bars/')
        self.assertIn('bazes', foo['links'])
        self.assertEquals(foo['links']['bazes']['href'], '/foos/42/bazes/')


class HttpRequestTests(unittest.TestCase):
    def test_default_values(self):
        request = HttpRequest('/')
        self.assertEquals(request.get_url(), '/')
        self.assertEquals(request.get_method(), 'GET')
        self.assertEquals(request.get_body(), '')

    def test_custom_method(self):
        request = HttpRequest('/', 'POST')
        self.assertEquals(request.get_method(), 'POST')


class ResourceBuilderTests(unittest.TestCase):
    def setUp(self):
        transport = MockTransport()
        transport.set_resource('/foos/1/',  {'prop': 'x'})
        transport.set_resource('/foos/2/',  {'prop': 'y'})
        transport.set_resource('/foos/3/',  {'prop': 'z'})
        transport.set_resource('/bars/1/',  {'field': 'foo'})
        transport.set_resource('/bars/2/',  {'field': 'bar'})
        transport.set_resource('/bars/3/',  {'field': 'baz'})
        transport.set_resource('/foos/1/bazes/1/',  {'attr': '101'})
        transport.set_resource('/foos/2/bazes/2/',  {'attr': '102'})
        transport.set_resource('/foos/3/bazes/3/',  {'attr': '103'})
        transport.set_resource('/foos/3/bazes/3/quxes/1/',  {'value': 'name'})

        transport.set_resource('/reqs/1/', {'author': 'user1', 'group': 'dev'})
        transport.set_resource('/reqs/2/', {'author': 'user2', 'group': 'gfx'})
        transport.set_resource('/reqs/3/', {'author': 'user3', 'group': 'sfx'})
        transport.set_resource('/reqs/1/revs/', {'file': 'main.cpp'})
        transport.set_resource('/reqs/2/revs/', {'file': 'layout.svg'})
        transport.set_resource('/reqs/3/revs/', {'file': 'ambient.wav'})

        self.transport = transport
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
