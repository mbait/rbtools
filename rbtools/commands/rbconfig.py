import optparse

from rbtools.api.settings import Settings


def main():
    p = optparse.OptionParser(prog='rb config')

    p.add_option('-u', '--user', dest='user', help='user name')
    p.add_option('-U', '--url', dest='server_url',
                 help='URL of ReviewBoard server')
    p.add_option('-c', '--cookie-file', action='store', dest='cookie')

    opts, args = p.parse_args()
    values = {
            'user_name' : opts.user,
            'server_url' : opts.server_url,
            'cookie' : opts.cookie
            }
    # filter out those values are None
    valid = [ (name, values[name]) for name in values if values[name] ]

    settings = Settings()
    if len(valid):
        for opt in valid:
            name, value = opt
            settings.add_setting(name, value)
        settings.save()
    else:
        p.print_usage()


if __name__ == "__main__":
    main()
