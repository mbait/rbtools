import cookielib
import getpass
import mimetools
import mimetypes
import os
import urllib2
from urlparse import urlparse

from rbtools import get_package_version


class PasswordMgr(urllib2.HTTPPasswordMgr):
    """ Adds HTTP authentication support for URLs.

    Python 2.4's password manager has a bug in http authentication when the
    target server uses a non-standard port.  This works around that bug on
    Python 2.4 installs. This also allows post-review to prompt for passwords
    in a consistent way.

    See: http://bugs.python.org/issue974757
    """
    def find_user_password(self, realm, uri):
        if uri.startswith(self.rb_url):
            if self.rb_user is None or self.rb_pass is None:
                self.rb_user, self.rb_pass = \
                    self.password_inputer.get_user_password(realm,
                                                            urlparse(uri)[1])

            return self.rb_user, self.rb_pass
        else:
            # If this is an auth request for some other domain (since HTTP
            # handlers are global), fall back to standard password management.
            return urllib2.HTTPPasswordMgr.find_user_password(self, realm, uri)


class ServerInterface(object):
    """ An object used to make HTTP requests to a ReviewBoard server.

    A class which performs basic communication with a ReviewBoard server and
    tracks cookie information.
    """
    def __init__(self, server_url, cookie_path_file=None, password_mgr=None):
        self.server_url = server_url

        if cookie_path_file:
            self.cookie_file = cookie_path_file
            #if not os.path.isfile(cookie_path_file):
            #    temp_file = open(cookie_path_file, 'w')
            #    temp_file.close()

            #self.cookie_file = cookie_path_file
        else:
            self.cookie_file = '.default_cookie'

        if password_mgr and \
            isinstance(password_mgr, PasswordMgr):
            self.password_mgr = password_mgr
        else:
            self.password_mgr = PasswordMgr(self.server_url)

        self.cookie_jar = cookielib.MozillaCookieJar(self.cookie_file)

        if os.path.isfile(self.cookie_file):
            self.cookie_jar.load()

        cookie_handler = urllib2.HTTPCookieProcessor(self.cookie_jar)
        basic_auth_handler = urllib2.HTTPBasicAuthHandler(self.password_mgr)
        digest_auth_handler = urllib2.HTTPDigestAuthHandler(self.password_mgr)
        opener = urllib2.build_opener(cookie_handler,
                                      basic_auth_handler,
                                      digest_auth_handler)
        opener.addheaders = [
            ('User-agent', 'RBTools/' + get_package_version())
        ]
        urllib2.install_opener(opener)

    def _encode_multipart_formdata(self, fields={}, files={}):
        """ Encodes data for use in an HTTP request.

        Paramaters:
            fields - the fields to be encoded.  This should be a dict in a
                     key:value format
            files  - the files to be encoded.  This should be a dict in a
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
            lines.append('Content-Type: %s' % self._get_content_type(filename))
            lines.append('')
            lines.append(content)

        return ('multipart/form-data; boundary="%s"' % boundary,
               '\r\n'.join(lines))

    def _get_content_type(filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

    def has_valid_cookie(self):
        """ Checks if a valid cookie already exists for to the RB server.

        Returns true if the ServerInterface can find and load a cookie for the
        server that has not expired.
        """
        parsed_url = urlparse(self.server_url)
        host = parsed_url[1]
        host = host.split(":")[0]
        path = parsed_url[2] or '/'

        try:
            self.cookie_jar.load(self.cookie_file, ignore_expires=True)

            try:
                cookie = self.cookie_jar._cookies[host][path]['rbsessionid']

                if not cookie.is_expired():
                    return True
            except KeyError:
                # Cookie file loaded, but no cookie for this server
                pass
        except IOError:
            # Couldn't load cookie file
            pass

        return False


def get_auth_data(realm, uri):
    print "Enter username and password for %s at %s" % (realm, uri)
    return raw_input('User: '), getpass.getpass('Password: ')
