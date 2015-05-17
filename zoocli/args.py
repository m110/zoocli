import argparse
from collections import namedtuple

from zoocli.config import config
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

        editor = self._add_command(config['zoocli']['editor'], "edit node's data in the best editor possible")
        editor.add_argument("path", nargs="?", help="node to be edited")

        create = self._add_command("create", "create new node")
        create.add_argument("path", nargs="?", default=None,  help="node path")
        create.add_argument("-e", action="store_true", help="ephemeral", dest="ephemeral")
        create.add_argument("-p", action="store_true", help="create parent nodes if needed", dest="makepath")
        create.add_argument("-s", action="store_true", help="sequence", dest="sequence")
        create.add_argument("data", nargs="?", default=None,  help="data to set")

        rm = self._add_command("rm", "remove node")
        rm.add_argument("-r", action="store_true", help="recursive", dest="recursive")
        rm.add_argument("path", nargs="?", default=None,  help="node path")

        stat = self._add_command("stat", "get node's details")
        stat.add_argument("path", nargs="?", default=None,  help="node path (defaults to current")

        getacl = self._add_command("getacl", "show node's ACL")
        getacl.add_argument("path", nargs="?", default=None,  help="node path (defaults to current")

        addacl = self._add_command("addacl", "add new ACL for node")
        addacl.add_argument("path", nargs="?", default=None,  help="node path")
        addacl.add_argument("permissions", nargs="?", default=None,  help="ACL permissions")
        addacl.add_argument("scheme", nargs="?", default=None,  help="ACL scheme")
        addacl.add_argument("id", nargs="?", default=None,  help="ACL id")

        rmacl = self._add_command("rmacl", "remove node's ACL")
        rmacl.add_argument("path", nargs="?", default=None,  help="node path")
        rmacl.add_argument("index", nargs="?", default=None, help="ACL index")

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
