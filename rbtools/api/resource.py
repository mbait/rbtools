class Resource(object):
    """ Defines common methods for working with a resource.

    If a particular resource has special methods (like 'Diff Resource') its
    binding must be implemented as a sub-class of this class and then
    registered in the RBClient instance.
    """
    def __init__(self):
        object.__setattr__(self, '_fields', {})

    def __getattr__(self, name):
        return self._fields[name]

    def __setattr__(self, name, value):
        object.__getattribute__(self, '_fields').__setitem__(name, value)


class ResourceList(Resource):
    """ Provides pagination for the 'list' resource kinds.

    Although it acts as the iterator and fetches only a portion of resources at
    a time, the 'len' function will return actual number of child resources on
    the server.
    """
    def __len__(self):
        return self._total_results


class RootResource(Resource):
    """ Specialization of the Root List Resource.

    Provides additional methods for fetching any resource directly. In order to
    access a particular resource users should use names listed in
    'uri_templates' section of a sample Root Resource payload (see the web API
    documentation) with the 'get_' prefix.
    """
    def __getattr__(self, name):
        if name in self._uri_templates:
            return self._uri_templates
        else:
            return super(Resource, self).__getattr__(name)


class DiffResource(Resource):
    def get_patch(self):
        """ Returns unified diff content."""
        pass


class DiffListResource(ResourceList):
    def create(self, diff_path, parent_path=None):
        """ Uploads a new patch. Overrides default 'create' method.

        This will implicitly create new Review Request draft.
        """
        r = HttpRequest('POST')
        r.add_file('path', diff_path)

        if parent_path:
            r.add_file('parent_diff_path', parent_name)

        self.transport.send(r)

# vim: set ts=4 :
# vim: set sw=4 :
# vim: set expandtab :
