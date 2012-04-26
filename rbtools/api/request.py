import mimetools


class HttpRequest(object):
    """ High-level HTTP-request object."""
    def __init__(self, url, method='GET'):
        self._url = url
        self._method = method
        self._headers = {}
        self.fields = {}
        self.files = {}

    def get_url(self):
        return self._url

    def get_method(self):
        return self._method

    def has_header(self, name):
        return name in self._headers

    def set_header(self, name, value):
        self._headers[name] = value

    def get_body(self):
        """ Encodes data for use in an HTTP request.

        Paramaters:
            fields - the fields to be encoded.  This should be a dict in a
                     key:value format
            files  - the files to be encoded.  This should be a dict in a
                     key:dict, filename:value and content:value format
        """
        if not (self.fields or self.files):
            return ''

        NEWLINE = '\r\n'
        BOUNDARY = mimetools.choose_boundary()
        content = ''

        for key in self.fields:
            content += '--' + BOUNDARY + NEWLINE
            content += 'Content-Disposition: form-data; name="%s"' % key
            content += NEWLINE + NEWLINE
            content += self.fields[key] + NEWLINE

        for key in self.files:
            filename = self.files[key]['filename']
            value = self.files[key]['content']
            content += '--' + BOUNDARY + NEWLINE
            content += 'Content-Disposition: form-data; name="%s"; ' % key
            content += 'filename="%s"' % filename + NEWLINE
            content += NEWLINE
            content += value + NEWLINE

        content += '--' + BOUNDARY + '--' + NEWLINE + NEWLINE
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

        return content_type, content
