import getpass

try:
    from json import dumps
except ImportError:
    from simplejson import dumps


def json_to_string(json):
    return dumps(json, sort_keys=True, indent=4)
