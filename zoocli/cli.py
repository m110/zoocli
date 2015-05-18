import os
import shlex
import warnings
import readline
import traceback

from zoocli.args import Args
from zoocli.config import config
from zoocli.commands import ZooCLICommands
from zoocli.exceptions import UnknownCommand, CLIException
from zoocli.completer import Completer
from zoocli.paths import ROOT_PATH

warnings.simplefilter("ignore")

PROMPT = "> "


class ZooCLI(object):

    def __init__(self):
        self._running = True
        self._verbose = config.getboolean('zoocli', 'verbose')
        self._args = Args()
        self._commands = ZooCLICommands(self)
        self._completer = Completer(self)
        self._current_path = ROOT_PATH

        self._history_file = os.path.expanduser(config['zoocli'].get('history', ''))

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
                    self.execute(shlex.split(command))
            except UnknownCommand as exc:
                print(exc)
            except (KeyboardInterrupt, EOFError):
                self._running = False

        if self._history_file:
            readline.write_history_file(self._history_file)

        return 0

    def _format_prompt(self):
        return "[{path}]{prompt}".format(path=self._current_path,
                                         prompt=PROMPT)

    def execute(self, args):
        """Executes single command and prints result, if any."""
        command, kwargs = self.parse(args)

        try:
            result = self._commands.execute(command, **kwargs)
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

    def set_running(self, running):
        self._running = running

    def set_current_path(self, current_path):
        self._current_path = current_path

    @property
    def args(self):
        return self._args

    @property
    def commands(self):
        return self._commands

    @property
    def current_path(self):
        return self._current_path
