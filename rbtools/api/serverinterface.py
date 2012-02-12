import mimetools
import mimetypes

from rbtools.api.utils import TerminalAuthReader


class RBServer(object):
    """ An object used to make HTTP requests to a ReviewBoard server.

    A class which performs basic communication with a ReviewBoard server and
    tracks cookie information.
    """
    def __init__(self, url, cookie_file=None,
                 auth_reader=TerminalAuthReader()):
        self.url = url

    def _encode_multipart_formdata(self, fields=[], files=[]):
        """ Encodes data for use in an HTTP request.

        Paramaters:
            fields - the fields to be encoded.  This should be a list in a
                     key:value format
            files  - the files to be encoded.  This should be a list in a
                     key:filename:content format
        """
        CONTENT_HEADER = 'Content-Disposition: form-data'

        boundary = '--%s--' % mimetools.choose_boundary()
        lines = []

        for key, value in fields:
            lines.append(boundary)
            lines.append('%s; name="%s"' % (CONTENT_HEADER, key))
            lines.append('')
            lines.append(value)

        for key, filename, content in files:
            lines.append(boundary)
            lines.append('%s; name="%s"; filename="%s"' %
                         (CONTENT_HEADER, key, filename))
            lines.append('Content-Type: %s' %
                         mimetypes.guess_type(filename)[0]
                         or 'application/octet-stream')
            lines.append('')
            lines.append(content)

        return ('multipart/form-data; boundary="%s"' % boundary,
               '\r\n'.join(lines))
