"""API exceptions and request error wrappers."""
import sys
from inspect import getmembers, isclass


class APIError(Exception):
    def __init__(self, http_status, error_code, rsp=None, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.http_status = http_status
        self.error_code = error_code
        self.rsp = rsp

    def __str__(self):
        code_str = "HTTP %d" % self.http_status

        if self.error_code:
            code_str += ', API Error %d' % self.error_code

        if self.rsp and 'err' in self.rsp:
            return '%s (%s)' % (self.rsp['err']['msg'], code_str)
        else:
            return code_str


class ResourceError(Exception):
    def __init__(self, msg, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.msg = msg

    def __str__(self):
        return self.msg


class RequestError(Exception):
    """Base class for request errors.

    This exception is thrown when the returned payload is valid JSON object
    but its status is other than 'ok' (for now the only another value is
    'fail').

    See the following document for more info on request errors:
    http://www.reviewboard.org/docs/manual/dev/webapi/2.0/errors/"""
    pass


class UnknownRequestError(RequestError):
    """The error code returned in response is not known.

    This may occur due to updates of the API.
    """
    code = -1


class DoesNotExist(RequestError):
    """Resource does not exist.

    One or more of the IDs provided in the URL doesn't exist or isn't
    valid in that level of the resource tree.
    """
    code = 100


class PermissionDenied(RequestError):
    """Permission to resource denied.

    Your client doesn't have permission to access this resource or to
    perform the operation. Usually this means the user your client is
    logged in as just doesn't own the resource or doesn't have the access
    rights needed.
    """
    code = 101


class NotLoggedIn(RequestError):
    """Client is not logged in.

    The resource requires that your client is logged in, and you're not logged
    in yet. This is sent along with WWW-Authenticate HTTP headers.
    """
    code = 103


class LoginFailed(RequestError):
    """The client attempted to log in, but didn't provide valid credentials.

    You'll be provided with WWW-Authenticate HTTP headers so your client can
    try again.
    """
    code = 104


class InvalidFormData(RequestError):
    """The data sent to in request is invalid.

    The data sent in the request (usually when using HTTP PUT or POST) had
    errors. One or more fields failed to validate correctly.

    This comes with a fields key containing a mapping of field names to
    lists of error texts.
    """
    code = 105


class InvalidChangeNumber(RequestError):
    """Invalid change number specified for a new review request.

    The change number specified when creating a review request could not be
    found in the repository. This is used for repositories that keep track of
    changeset information server-side, such as Perforce.
    """
    code = 203


class ChangeNumberInUse(RequestError):
    """Change number specified in a review request is in use.

    The change number used to create a new review request wasn't valid, because
    another review request already exists with that change number. You will
    only see this with repositories that support server-side changesets, such
    as Perforce. Usually, the correct thing to do is to instead modify the
    other review request.
    """
    code = 204


class MissingRepository(RequestError):
    """Repository is missing at specified path.

    A repository path was specified that didn't seem to contain a valid
    repository.
    """
    code = 205


class InvalidRepository(RequestError):
    """The repository specified in the request isn't known by Review Board.

    The repository path or ID specified in the request isn't known by
    Review Board.

    This will provide a repository key containing the path
    or ID that failed.
    """
    code = 206


class RepositoryFileNotFound(RequestError):
    """The file included in review request is missing in the repository.

    A file specified in a request that should have been in the repository was
    not found there. This could be a problem with the path or the revision.

    This will provide file and revision keys containing the file path and
    revision that failed.
    """
    code = 207


class InvalidUser(RequestError):
    """The username specified in a request does not exist on the server.

    This isn't related to authentication, but rather for usernames that
    are passed as parameters in some request, such as when creating a review
    request as another user.
    """
    code = 208


class RepositoryActionNotSupported(RequestError):
    """Action is not supported by the remote repository.

    The request made on a repository's resource can't be performed by that
    type of repository. That particular action is invalid for that repository
    type. There is no sense in retrying this request on the same repository.
    """
    code = 209


class RepositoryInformationError(RequestError):
    """Repository information request is failed.

    The attempt to fetch server-side information on a repository failed due to
    some unknown reason. This may be a temporary outage. The request should be
    tried again, once you've checked that the repository's server is up and
    running.
    """
    code = 210


class EmptyChangeset(RequestError):
    """Server-side does not contain changed for the specified changeset.

    The change number provided for the request represents a server-side
    changeset that doesn't contain any files. You will only ever see this for
    repositories that implement server-side changesets, such as Perforce. Add
    some files to the changeset and try again.
    """
    code = 212


class ServerConfigurationError(RequestError):
    """Review Board server is misconfigured.

    Review Board attempted to store data in the database or a configuration
    file as needed to fulfill this request, but wasn't able to. The reason for
    this will be stored in reason.
    """
    code = 213


class BadHostKey(RequestError):
    """Unexpected SSH key is used for authentication.

    Review Board encountered an unexpected SSH key on host
    (typically a repository). The key found didn't match what Review Board had
    previously recorded.

    The hostname, key (in base64) and the key we expected to find
    (also in base64) will be returned along with the error.
    """
    code = 214


class UnverifiedHostKey(RequestError):
    """Unverified SSH key is used for authentication.

    Review Board encountered an unverified SSH key on another host
    (typically a repository). The key needs to be verified before Review Board
    can access the host.

    The hostname and key (in base64) will be returned along with the error.
    """
    code = 215


class UnverifiedHostCertificate(RequestError):
    """Unverified certificate is used in HTTPS request.

    Review Board encountered an unverified HTTPS certificate another host
    (typically a repository). The certificate needs to be verified before
    Review Board can access the host.

    The certificate information will be returned along with the error.
    """
    code = 216


class MissingUserKey(RequestError):
    """Repository denied authentication request due to SSH key missing.

    Review Board attempted to authenticate with a repository that required a
    public SSH key, but no SSH key was configured on Review Board.
    """
    code = 217


class RepositoryAuthenticationError(RequestError):
    """Repository denied authentication request from Review Board.

    Review Board attempted to authenticate with a repository, but the proper
    login information wasn't specified.

    The specific reason it failed is returned in reason along with the error.
    """
    code = 218


class ResponseError(Exception):
    """Base class for response errors.

    This exception is thrown when request that is likely to be correct fails.
    This may be due to network problems or unexpected response data (e.g.
    not JSON).
    """
    pass


class InvalidPayload(ResponseError):
    """Response payload has invalid format."""
    pass


class TokenNotFound(ResponseError):
    """Expected token was not found in response payload."""
    pass


class InvalidTokenType(ResponseError):
    """Token is in payload, but has neigther list nor dict type."""
    pass


def get_exception_by_code(code):
    """Return API error wrapping class by the error code."""
    try:
        return request_errors[code]
    except KeyError:
        return UnknownRequestError


request_errors = dict([(cls.code, cls)
                       for name, cls in getmembers(sys.modules[__name__])
                       if isclass(cls) and cls != RequestError and
                          issubclass(cls, RequestError)])
