from rbtools.api.resource import DiffResource, RootResource


class RBClient(object):
    """ Entry point for accessing RB resources through the web API.
    """
    def __init__(self, url, bindings):
        bindings = {
            '/': RootResource,
            '/review-requests/*/diffs/': DiffResource
        }.update(bindings)

    def get_root(self, callback):
        pass

    def get_root_sync(self):
        pass
