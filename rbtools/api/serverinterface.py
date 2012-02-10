import cookielib
import mimetools
import mimetypes
import os
import urllib2
from urlparse import urlparse

from rbtools import get_package_version
from rbtools.api.utils import TerminalAuthReader


class RBServer(object):
    """ An object used to make HTTP requests to a ReviewBoard server.

    A class which performs basic communication with a ReviewBoard server and
    tracks cookie information.
    """
    class PasswordMgr(urllib2.HTTPPasswordMgr):
        """ Adds HTTP authentication support for URLs.

        Python 2.4's password manager has a bug in http authentication when the
        target server uses a non-standard port.  This works around that bug on
        Python 2.4 installs. This also allows post-review to prompt for
        passwords in a consistent way.

        See: http://bugs.python.org/issue974757
        """
        def __init__(self, reader):
            super(RBServer.PasswordMgr, self).__init__()
            self.user = None
            self.password = None
            self.auth_reader = reader

        def find_user_password(self, realm, uri):
            if uri.startswith(self.url):
                if self.rb_user is None or self.rb_pass is None:
                    self.user, self.password =\
                        self.auth_reader.get_auth_data(realm, urlparse(uri)[1])

                return self.user, self.password
            else:
                # If this is an auth request for some other domain (since HTTP
                # handlers are global), fall back to standard password
                # management.
                return urllib2.HTTPPasswordMgr.find_user_password(self,
                                                                  realm, uri)

    def __init__(self, url, cookie_file=None,
                 auth_reader=TerminalAuthReader()):
        self.url = url
        self.pass_mgr = RBServer.PasswordMgr(auth_reader)

        if cookie_file:
            self.cookie_file = cookie_file
            #if not os.path.isfile(cookie_path_file):
            #    temp_file = open(cookie_path_file, 'w')
            #    temp_file.close()

            #self.cookie_file = cookie_path_file
        else:
            self.cookie_file = '.default_cookie'

        self.cookie_jar = cookielib.MozillaCookieJar(self.cookie_file)

        if os.path.isfile(self.cookie_file):
            self.cookie_jar.load()

        cookie_handler = urllib2.HTTPCookieProcessor(self.cookie_jar)
        basic_auth_handler = urllib2.HTTPBasicAuthHandler(self.pass_mgr)
        digest_auth_handler = urllib2.HTTPDigestAuthHandler(self.pass_mgr)
        opener = urllib2.build_opener(cookie_handler, basic_auth_handler,
                                      digest_auth_handler)
        opener.addheaders = [
            ('User-agent', 'RBTools/' + get_package_version())
        ]
        urllib2.install_opener(opener)

    def _encode_multipart_formdata(self, fields={}, files={}):
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
