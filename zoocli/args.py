import argparse
from collections import namedtuple

from zoocli.exceptions import UnknownCommand

Command = namedtuple("Command", ['name', 'parser'])


class ArgsParser(argparse.ArgumentParser):

    def error(self, message):
        raise UnknownCommand(self.format_help().strip())


class Args(object):

    def __init__(self):
        self._commands = []

        self._parser = ArgsParser(add_help=False)
        self._commands_parser = self._parser.add_subparsers(help="command")

        ls = self._add_command("ls", "list resources")
        ls.add_argument("-l", action="store_true", help="long listing", dest="long")
        ls.add_argument("path", nargs="?", default=None,  help="node path (defaults to current)")

        cd = self._add_command("cd", "change current path")
        cd.add_argument("path", nargs="?", default=None,  help="node path (defaults to /)")

        get = self._add_command("get", "get node's data")
        get.add_argument("path", nargs="?", default=None,  help="node path (defaults to current")

        set = self._add_command("set", "set node's data")
        set.add_argument("path", nargs="?", default=None,  help="node path")
        set.add_argument("data", nargs="?", default=None,  help="data to set")

        help = self._add_command("help", "show this help",
                                 parser=self._parser, all_commands=self._commands)
        help.add_argument("subject", nargs="?", default=None)

        self._add_command("exit", "exit console")

        # Store all subparsers for improved help messages and completion support
        actions = [action for action in self._parser._actions
                   if isinstance(action, argparse._SubParsersAction)]
        self._commands.extend([Command(choice, subparser)
                               for action in actions
                               for choice, subparser in action.choices.items()])

    def _add_command(self, name, help, **kwargs):
        command = self._commands_parser.add_parser(name, help=help, add_help=False)
        command.set_defaults(command=name, **kwargs)
        return command

    def parse(self, args):
        return self._parser.parse_args(args)

    @property
    def commands(self):
        return self._commands
