import optparse

from rbtools.api.settings import Settings


def main():
    p = optparse.OptionParser(prog='rb config')

    p.add_option('-u', '--user', action='store', dest='user', help='user name')
    p.add_option('-U', '--url', action='store', dest='server_url',
                 help='path to ReviewBoard server')
    p.add_option('-c', '--cookie-file', action='store', dest='cookie')

    opts, args = p.parse_args()
    settings = Settings()
    has_options = False
    if opts.user:
        settings.add_setting('user_name', opts.user)
        has_options = True
    if opts.server_url:
        settings.add_setting('server_url', opts.server_url)
        has_options = True
    if opts.cookie:
        settings.add_setting('cookie', opts.cookie)
        has_options = True

    if has_options:
        settings.save()
    else:
        p.print_usage()


if __name__ == "__main__":
    main()
