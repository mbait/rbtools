import sys

from optparse import IndentedHelpFormatter, OptionParser

from rbtools import get_version_string
from rbtools.api.utilities import RBUtilities
from rbtools.commands import RB_CMD_PATTERN, RB_COMMANDS, RB_MAIN


_COMMANDS_LIST_STR = 'Avaiable commands are:'


# TODO:
# move this into rbtools/util at mering the branch
# where such hierachy already exists
class ImprovedFormatter(IndentedHelpFormatter):
    def format_description(self, description):
        if description:
            return description + '\n'
        else:
            return ''


def main():
    parser = OptionParser(prog=RB_MAIN, usage='%prog <command> [<args>]',
                          formatter=ImprovedFormatter(),
                          description=_COMMANDS_LIST_STR,
                          version='RBTools %s' % (get_version_string()))
    parser.disable_interspersed_args()
    opt, args = parser.parse_args()

    if not args:
        parser.print_help()
        sys.exit(1)

    cmd = filter(lambda x: RB_MAIN + args[0] == x[0], RB_COMMANDS)
    if cmd:
        util = RBUtilities()
        args[0] = RB_CMD_PATTERN % (args[0])
        print util.safe_execute(args)
    else:
        parser.error("'%s' is not a command" % (args[0]))


_indent = max(map(lambda x: len(x[0]), RB_COMMANDS)) - len(RB_MAIN)
for cmd, desc in RB_COMMANDS:
    _COMMANDS_LIST_STR += '\n  %-*s  %s' % (_indent, cmd[len(RB_MAIN):], desc)

if __name__ == "__main__":
    main()
