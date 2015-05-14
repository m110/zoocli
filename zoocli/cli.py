import os
import atexit
import warnings
import readline
import traceback

from zoocli.args import Args
from zoocli.config import config
from zoocli.exceptions import UnknownCommand, CLIException
from zoocli.zookeeper import ZooKeeper
from zoocli.completer import Completer
from zoocli.paths import ROOT_PATH, format_path

warnings.simplefilter("ignore")

PROMPT = "> "


class ZooCLI(object):

    def __init__(self):
        self._running = True
        self._verbose = config.getboolean('zoocli', 'verbose')
        self._args = Args()
        self._completer = Completer(self)

        self._zookeeper = ZooKeeper()
        atexit.register(self._zookeeper.stop)

        self._current_path = ROOT_PATH

        self._history_file = os.path.expanduser(config['zoocli'].get('history', ''))

        self._commands_map = {
            'ls': self.ls,
            'cd': self.cd,
            'help': self.help,
            'exit': self.exit,
        }

    def run(self):
        """Loops and executes commands in interactive mode."""
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self._completer.complete)

        if self._history_file:
            # Ensure history file exists
            if not os.path.isfile(self._history_file):
                open(self._history_file, 'w').close()

            readline.read_history_file(self._history_file)

        while self._running:
            try:
                command = input(self._format_prompt())
                if command:
                    self.execute(command.split())
            except UnknownCommand as exc:
                print(exc)
            except (KeyboardInterrupt, EOFError):
                self._running = False

        if self._history_file:
            readline.write_history_file(self._history_file)

        return 0

    def execute(self, args):
        """Executes single command and prints result, if any."""
        command, kwargs = self.parse(args)

        if command not in self._commands_map:
            raise UnknownCommand("There is no action for command {}".format(command))

        method = self._commands_map[command]

        try:
            result = method(**kwargs)
            if result:
                print(result)
            return 0
        except CLIException as exc:
            print(exc)
            return 1
        except Exception:
            traceback.print_exc()
            return 2

    def parse(self, args):
        parsed = self._args.parse(args)
        kwargs = dict(parsed._get_kwargs())

        command = kwargs.pop('command')

        return command, kwargs

    def log(self, message, *args, **kwargs):
        if self._verbose:
            print(message.format(*args, **kwargs))

    def ls(self, long=False, path=None):
        path = format_path(self._current_path, path)
        result = self._zookeeper.list(path)

        separator = "\n" if long else " "
        return separator.join(sorted(result))

    def cd(self, path=None):
        path = format_path(self._current_path, path, default=ROOT_PATH)

        # No exception means correct path
        self._zookeeper.list(path)
        self._current_path = path

    def help(self, parser, all_commands, subject):
        if subject:
            subparsers = [command for command in all_commands
                          if command.name == subject]
            if subparsers:
                parser = subparsers[0].parser

        return parser.print_help()

    def exit(self):
        self._running = False

    def _format_prompt(self):
        return "[{path}]{prompt}".format(path=self._current_path,
                                         prompt=PROMPT)

    @property
    def commands(self):
        return self._args.commands
