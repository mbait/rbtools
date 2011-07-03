import optparse

from rbtools.api.settings import Settings


def main():
    p = optparse.OptionParser(prog='rb config')

    p.add_option('-u', '--user', dest='user', help='user name')
    p.add_option('-U', '--url', dest='server_url',
                 help='Review Board server URL')
    p.add_option('-c', '--cookie-file', action='store', dest='cookie',
                 help='a file to store user session cookies')
    p.add_option('--global', action='store_true', dest='is_global',
                 help='use global config file')

    opts, args = p.parse_args()
    values = {
        'user' : opts.user,
        'reviewboard_url' : opts.server_url,
        'cookie_file' : opts.cookie
    }
    # Filter out the values that are None.
    valid = [(name, values[name])
             for name in values if values[name] is not None]

    settings = Settings()
    if valid:
        for name, value in valid:
            print "%s : %s" % (name, value)
            setattr(settings, name, value)

        if opts.is_global:
            settings.save_global()
        else:
            settings.save_local()
    else:
        p.print_usage()


if __name__ == "__main__":
    main()
