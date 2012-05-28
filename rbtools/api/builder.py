class ResourceBuilder(object):
    LINKS_TOK = 'links'

    _EXCLUDE_ATTRS = [LINKS_TOK, 'stat']

    def __init__(self, transport_cls):
        self._transport_cls = transport_cls

    def create_request(self, request, token=None):
        return self._transport_cls((request, token))

    def create_resource(self, payload, transport_cls, token=None):
        payload = 
        excluded = self._EXCLUDE_ATTRS[:]
        # Root and all List resources do not have tokens.
        if token:
            if isinstance(payload[token], list):
                # Must be a list resource.
                excluded.append(token)

                for child in payload[token]:
                    # TODO: build child resources
                    pass
            else:
                # Non-root resource.
                payload = payload[token]

        # Inject fields.
        for name, value in payload.iteritems():
            if name in excluded:
                continue

            setattr(resource, name, value)

        # Inject methods.
        for name, attrs in payload[self.LINKS_TOK]:
            setattr(resource, name, 'x')

        return resource

# vim: set ts=4 :
# vim: set sw=4 :
# vim: set expandtab :
