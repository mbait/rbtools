import logging
import os
import socket

from rbtools.clients import SCMClient, RepositoryInfo
from rbtools.util.check import check_install
from rbtools.util.process import execute


class CVSClient(SCMClient):
    """
    A wrapper around the cvs tool that fetches repository
    information and generates compatible diffs.
    """
    def __init__(self, **kwargs):
        super(CVSClient, self).__init__(**kwargs)

    def get_repository_info(self):
        if not check_install("cvs"):
            return None

        cvsroot_path = os.path.join("CVS", "Root")

        if not os.path.exists(cvsroot_path):
            return None

        fp = open(cvsroot_path, "r")
        repository_path = fp.read().strip()
        fp.close()

        i = repository_path.find("@")
        if i != -1:
            repository_path = repository_path[i + 1:]

        i = repository_path.rfind(":")
        if i != -1:
            host = repository_path[:i]
            try:
                canon = socket.getfqdn(host)
                repository_path = repository_path.replace('%s:' % host,
                                                          '%s:' % canon)
            except socket.error, msg:
                logging.error("failed to get fqdn for %s, msg=%s"
                              % (host, msg))

        return RepositoryInfo(path=repository_path)

    def diff(self, files):
        """
        Performs a diff across all modified files in a CVS repository.

        CVS repositories do not support branches of branches in a way that
        makes parent diffs possible, so we never return a parent diff
        (the second value in the tuple).
        """
        return (self.do_diff(files), None)

    def diff_between_revisions(self, revision_range, args, repository_info):
        """
        Performs a diff between 2 revisions of a CVS repository.
        """
        revs = []

        for rev in revision_range.split(":"):
            revs += ["-r", rev]

        return (self.do_diff(revs + args), None)

    def do_diff(self, params):
        """
        Performs the actual diff operation through cvs diff, handling
        fake errors generated by CVS.
        """
        # Diff returns "1" if differences were found.
        return execute(["cvs", "diff", "-uN"] + params,
                        extra_ignore_errors=(1,))
