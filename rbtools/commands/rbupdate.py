import sys

from optparse import OptionGroup, OptionParser


def main():
    parser = OptionParser(prog='rb update',
            usage='%prog [options] <request-id>')

    group = OptionGroup(parser, 'Actions')
    group.add_option('-s', '--submit', action='store_const',
            const='submitted', dest='close',
            help='close review request making submitted')
    group.add_option('-d', '--discard', action='store_const',
            const='discarded', dest='close',
            help='close review request making discarded')
    group.add_option('-o', '--open', action='store_const',
            const='pending', dest='close',
            help='open previously closed review request')
    group.add_option('-p', '--publish', action='store_true',
            help='publish review request')
    parser.add_option_group(group)

    group = OptionGroup(parser, 'Modifiers')
    group.add_option('-u', '--users', help='comma-separated list of reviewers')
    group.add_option('-g', '--groups',
            help='comma-separated list of review groups')
    group.add_option('-S', '--summary')
    group.add_option('-D', '--description')
    group.add_option('-t', '--testing-done')
    parser.add_option_group(group)

    opt, args = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
