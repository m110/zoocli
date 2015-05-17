import os
import shlex
import atexit
import tempfile
import warnings
import readline
import traceback

from zoocli.args import Args
from zoocli.config import config
from zoocli.exceptions import UnknownCommand, CLIException
from zoocli.zookeeper import ZooKeeper
from zoocli.completer import Completer
from zoocli.paths import ROOT_PATH, format_path
from zoocli.utils import timestamp_to_date

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
            'get': self.get,
            'set': self.set,
            config['zoocli']['editor']: self.editor,
            'create': self.create,
            'rm': self.rm,
            'stat': self.stat,
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
                    self.execute(shlex.split(command))
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

    def get(self, path=None):
        path = format_path(self._current_path, path)

        data = self._zookeeper.get(path)
        return data

    def set(self, path=None, data=None):
        if not path:
            raise CLIException("Missing node path")

        if not data:
            raise CLIException("Missing data")

        path = format_path(self._current_path, path)

        self._zookeeper.set(path, data)
        self.log("Set {} data: {}".format(path, data))

    def editor(self, path):
        path = format_path(self._current_path, path)
        data = self._zookeeper.get(path)

        tmp_file = tempfile.mktemp()

        with open(tmp_file, 'w') as file:
            file.write(data)

        command = "{} {}".format(config['zoocli']['editor'], tmp_file)
        exit_status = os.system(command)

        if not exit_status:
            self.log("Updating: {}".format(path))

            with open(tmp_file, 'r') as file:
                new_data = file.read().rstrip()
                self._zookeeper.set(path, new_data)

        os.unlink(tmp_file)

    def create(self, path=None, data=None, ephemeral=False, sequence=False, makepath=False):
        if not path:
            raise CLIException("Missing node path")

        path = format_path(self._current_path, path)

        self._zookeeper.create(path, data, ephemeral, sequence, makepath)
        self.log("Created: {}".format(path))

    def rm(self, path=None, recursive=False):
        if not path:
            raise CLIException("Missing node path")

        path = format_path(self._current_path, path)

        self._zookeeper.delete(path, recursive)
        self.log("Removed: {}".format(path))

    def stat(self, path=None):
        path = format_path(self._current_path, path)

        stat = self._zookeeper.stat(path)

        lines = ["Created: {created} by session id: {created_id}",
                 "Modified: {modified} by session id: {modified_id}",
                 "Children count: {children}",
                 "Data length: {data_length}",
                 "Ephemeral owner: {owner}",
                 "Version: {version}",
                 "ACL version: {aversion}",
                 "Children version: {cversion}",
                 "pzxid: {pzxid}"]

        return "\n".join(lines).format(
            version=stat.version,
            aversion=stat.acl_version,
            cversion=stat.children_version,
            created=timestamp_to_date(stat.created),
            created_id=stat.creation_transaction_id,
            modified=timestamp_to_date(stat.last_modified),
            modified_id=stat.last_modified_transaction_id,
            owner=stat.owner_session_id,
            data_length=stat.data_length,
            children=stat.children_count,
            pzxid=stat.pzxid,
        )

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
