import sys

from optparse import OptionParser

from rbtools.api.settings import Settings


def main():
    parser = OptionParser(prog='rb patch',
                          usage='%prog [options] <request-id>')

    parser.add_option('-r', '--revision', help='diff revision number')
    parser.add_option('-s', '--summary', action='store_true',
                      help='use request summary as commit message')
    parser.add_option('-d', '--description', action='store_true',
                      help='use request description as commit message')

    opt, args = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(1)

    if len(args) > 1:
        parser.error('unexpected arguments - %s' % args[1:])

    settings = Settings()
    settings.load()
    print '%s/api/review-requests/%s/diffs/%s/' % (settings.reviewboard_url,
                                                   args[0], opt.revision)

    #valid = False
    #settings = Settings()
    #settings.load()

    #if len(sys.argv) > 1:
    #    valid = True
    #    cookie = settings.get_cookie_file()
    #    server_url = settings.get_server_url()
    #    diff_file_name = 'patch_diff'
    #    arg_index = 1        
    #    commit = False

    #    if sys.argv[arg_index] == COMMIT_OPTION:
    #        if len(sys.argv) > 2:
    #            commit = True
    #            arg_index = arg_index + 1
    #        else:
    #            valid = False

    #    review_request_id = sys.argv[arg_index]
    #    arg_index = arg_index + 1
    #    server = ServerInterface(server_url, cookie)
    #    root = RootResource(server, server_url + 'api/')
    #    review_requests = root.get('review_requests')
    #    request = ReviewRequest(review_requests.get(review_request_id))
    #    diffs = request.get_or_create('diffs')
    #    revision_id = len(diffs)

    #    if len(sys.argv) > arg_index:
    #        if sys.argv[arg_index].isdigit():
    #            revision_id = sys.argv[arg_index]
    #        
    #    try:
    #        diff = DiffResource(diffs.get(revision_id))
    #    except HTTPError, e:
    #        if e.code == 404:
    #            print 'The specified diff revision ' \
    #                  'does not exist.'
    #            exit()
    #        else:
    #            raise e

    #    server_diff = diff.get_diff()
    #    diff_file = open(diff_file_name, 'w')

    #    if diff_file < 0:
    #        print 'could not open "' + diff_file_name + '" for writing.'
    #        exit()

    #    diff_file.write(server_diff)
    #    diff_file.close()
    #    client = get_client(server_url)
    #    client.apply_patch(diff_file_name, commit)

    #if not valid:
    #    print 'usage: rb patch [-c] ' \
    #          '<review_request_id> [revision_id]'
    #    print ''
    #    print '[-c] is used to commit the patch, in addition to applying it.'
    #    print '[file_name] can be used to set the name of the file to save ' \
    #          'the patch to.'
    #    print '[revision_id] may be specified to indicate which revision ' \
    #          'of the patch in the review request to use.  If unspecified ' \
    #          'the most recent revision is used.'


if __name__ == '__main__':
    main()
