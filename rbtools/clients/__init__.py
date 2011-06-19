import sys

from rbtools.clients.clearcase import ClearCaseClient
from rbtools.clients.cvs import CVSClient
from rbtools.clients.git import GitClient
from rbtools.clients.mercurial import MercurialClient
from rbtools.clients.perforce import PerforceClient
from rbtools.clients.plastic import PlasticClient
from rbtools.clients.svn import SVNClient

SCMCLIENTS = (
    CVSClient(),
    ClearCaseClient(),
    GitClient(),
    MercurialClient(),
    PerforceClient(),
    PlasticClient(),
    SVNClient(),
)


def scan_usable_client(options):
    repository_info = None
    tool = None

    # Try to find the SCM Client we're going to be working with.
    for tool in SCMCLIENTS:
        repository_info = tool.get_repository_info()

        if repository_info:
            break

    if not repository_info:
        if options.repository_url:
            print "No supported repository could be access at the supplied url."
        else:
            print "The current directory does not contain a checkout from a"
            print "supported source code repository."
        sys.exit(1)

    # Verify that options specific to an SCM Client have not been mis-used.
    if options.change_only and not repository_info.supports_changesets:
        sys.stderr.write("The --change-only option is not valid for the "
                         "current SCM client.\n")
        sys.exit(1)

    if options.parent_branch and not repository_info.supports_parent_diffs:
        sys.stderr.write("The --parent option is not valid for the "
                         "current SCM client.\n")
        sys.exit(1)

    if ((options.p4_client or options.p4_port) and \
        not isinstance(tool, PerforceClient)):
        sys.stderr.write("The --p4-client and --p4-port options are not valid "
                         "for the current SCM client.\n")
        sys.exit(1)

    return (repository_info, tool)
