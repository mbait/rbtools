from rbtools.api.builder import ResourceBuilder
from rbtools.utils.testbase import RBTestBase

class StubTransport(object):
    pass


class ResourceGeneratorTests(RBTestBase):
    def setUp(self):
        self.builder = ResourceBuilder(StubTransport())

    def testGetRoot(self):
        pass
