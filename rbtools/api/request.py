import mimetools
import urllib2


DEFAULT_MIME_TYPE = 'application/json'
CONTENT_TYPE_HEADER = 'Content-Type'


class Request(object):
    """Contains information about particular resource requests.

    RequestTransport implementaions must know how to convert this into their
    native request representation (like urllib2.Request)."""
    def __init__(self, url, method='GET', headers={}):
        self.url = url
        self.method = method
        self.headers = headers
        self.payload = None

    def set_header(self, name, value):
        self.headers[name] = value

    def set_payload(self, payload, mime_type=DEFAULT_MIME_TYPE):
        self.payload = payload
        self.set_header(CONTENT_TYPE_HEADER, mime_type)


class RequestTransport(object):
    """High-level interface for making HTTP requests."""
    def _encode_multipart_formdata(self, fields=None, files=None):
        """
        Encodes data for use in an HTTP request.

        Paramaters:
            fields - the fields to be encoded.  This should be a dict in a
                     key:value format
            files  - the files to be encoded.  This should be a dict in a
                     key:dict, filename:value and content:value format
        """
        BOUNDARY = mimetools.choose_boundary()
        content = ""

        fields = fields or {}
        files = files or {}

        for key in fields:
            content += "--" + BOUNDARY + "\r\n"
            content += "Content-Disposition: form-data; name=\"%s\"\r\n" % key
            content += "\r\n"
            content += fields[key] + "\r\n"

        for key in files:
            filename = files[key]['filename']
            value = files[key]['content']
            content += "--" + BOUNDARY + "\r\n"
            content += "Content-Disposition: form-data; name=\"%s\"; " % key
            content += "filename=\"%s\"\r\n" % filename
            content += "\r\n"
            content += value + "\r\n"

        content += "--" + BOUNDARY + "--\r\n"
        content += "\r\n"

        content_type = "multipart/form-data; boundary=%s" % BOUNDARY

        return content_type, content


class ThreadedRequestTransport(RequestTransport):
    """Perfroms HTTP requests using urllib2 library.

    As urllib2 does not support asynchronous IO this uses threads to emulate
    it. Full-featured asynchronous transport will be implemented later.
    """
    class RequestWithMethod(urllib2.Request):
        """Wrapper class for urllib2.Request.

        This allows for using PUT and DELETE, in addition to POST and GET.
        """
        def __init__(self, *args, **kwargs):
            urllib2.Request.__init__(self, *args, **kwargs)

        def get_method(self):
            return (self.method or
                    super(ThreadedRequestTransport.RequestWithMethod,
                          self).get_method())

    def __init__(self, cookie_path_file=None, password_mgr=None):
        #self.server_url = server_url

        #if cookie_path_file:
        #    self.cookie_file = cookie_path_file
        #    #if not os.path.isfile(cookie_path_file):
        #    #    temp_file = open(cookie_path_file, 'w')
        #    #    temp_file.close()
        #    #self.cookie_file = cookie_path_file
        #else:
        #    self.cookie_file = '.default_cookie'

        #self.cookie_jar = cookielib.MozillaCookieJar(self.cookie_file)

        #if os.path.isfile(self.cookie_file):
        #    self.cookie_jar.load()

        #cookie_handler = urllib2.HTTPCookieProcessor(self.cookie_jar)
        #basic_auth_handler = urllib2.HTTPBasicAuthHandler(self.password_mgr)
        #digest_auth_handler = urllib2.HTTPDigestAuthHandler(self.password_mgr)
        #opener = urllib2.build_opener(cookie_handler,
        #                              basic_auth_handler,
        #                              digest_auth_handler)
        #opener.addheaders = [
        #    ('User-agent', 'RBTools/' + get_package_version())
        #]
        #urllib2.install_opener(opener)
        super(ThreadedRequestTransport, self).__init__()

    def has_valid_cookie(self):
        """Checks if a valid cookie already exists for to the RB server.

        Returns true if the ServerInterface can find and load a cookie for the
        server that has not expired.
        """
        #parsed_url = urlparse(self.server_url)
        #host = parsed_url[1]
        #host = host.split(":")[0]
        #path = parsed_url[2] or '/'

        #try:
        #    self.cookie_jar.load(self.cookie_file, ignore_expires=True)

        #    try:
        #        cookie = self.cookie_jar._cookies[host][path]['rbsessionid']

        #        if not cookie.is_expired():
        #            return True
        #    except KeyError:
        #        # Cookie file loaded, but no cookie for this server
        #        pass
        #except IOError:
        #    # Couldn't load cookie file
        #    pass

        #return False
        pass

    def _native_request(self, request):
        return ThreadedRequestTransport.RequestWithMethod(request.url,
                                                          request.payload,
                                                          request.headers)

    def send(self, request):
        r = urllib2.urlopen(self._native_request(request))
        return r.read()

    def send_async(self, request, on_success, on_failure=None):
        pass
