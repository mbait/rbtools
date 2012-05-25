import json


class JsonFormat(object):
    def mime_type(self):
        return 'application/json'

    def encode(self, obj):
        return json.dumps(obj)

    def decode(self, payload):
        return json.loads(payload)

# vim: set ts=4 :
# vim: set sw=4 :
# vim: set expandtab :
