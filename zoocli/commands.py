import os
import atexit
import tempfile

from zoocli.config import config
from zoocli.exceptions import UnknownCommand, CLIException
from zoocli.paths import ROOT_PATH, format_path
from zoocli.utils import timestamp_to_date
from zoocli.zookeeper import ZooKeeper


class Commands(object):

    def __init__(self, cli):
        self._cli = cli
        self._commands = {}

    def execute(self, name, *args, **kwargs):
        if hasattr(self, name):
            method = getattr(self, name)
            if getattr(method, 'command', None):
                return method(*args, **kwargs)

        raise UnknownCommand("There is no action for command {}".format(command))


def command(function):
    function.command = True
    return function


class ZooCLICommands(Commands):

    def __init__(self, cli):
        super().__init__(cli)
        self._zookeeper = ZooKeeper()
        atexit.register(self._zookeeper.stop)

    @command
    def ls(self, long=False, path=None):
        path = format_path(self._cli.current_path, path)
        result = self._zookeeper.list(path)

        separator = "\n" if long else " "
        return separator.join(sorted(result))

    @command
    def cd(self, path=None):
        path = format_path(self._cli.current_path, path, default=ROOT_PATH)

        # No exception means correct path
        self._zookeeper.list(path)
        self._cli.set_current_path(path)

    @command
    def get(self, path=None):
        path = format_path(self._cli.current_path, path)

        data = self._zookeeper.get(path)
        return data

    @command
    def set(self, path=None, data=None):
        if not path:
            raise CLIException("Missing node path")

        if not data:
            raise CLIException("Missing data")

        path = format_path(self._cli.current_path, path)

        self._zookeeper.set(path, data)
        self._cli.log("Set {} data: {}".format(path, data))

    @command
    def editor(self, path):
        path = format_path(self._cli.current_path, path)
        data = self._zookeeper.get(path)

        tmp_file = tempfile.mktemp()

        with open(tmp_file, 'w') as file:
            file.write(data)

        cmd = "{} {}".format(config['zoocli']['editor'], tmp_file)
        exit_status = os.system(cmd)

        if not exit_status:
            self._cli.log("Updating: {}".format(path))

            with open(tmp_file, 'r') as file:
                new_data = file.read().rstrip()
                self._zookeeper.set(path, new_data)

        os.unlink(tmp_file)

    @command
    def create(self, path=None, data=None, ephemeral=False, sequence=False, makepath=False):
        if not path:
            raise CLIException("Missing node path")

        path = format_path(self._cli.current_path, path)

        self._zookeeper.create(path, data, ephemeral, sequence, makepath)
        self._cli.log("Created: {}".format(path))

    @command
    def rm(self, path=None, recursive=False):
        if not path:
            raise CLIException("Missing node path")

        path = format_path(self._cli.current_path, path)

        self._zookeeper.delete(path, recursive)
        self._cli.log("Removed: {}".format(path))

    @command
    def stat(self, path=None):
        path = format_path(self._cli.current_path, path)

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

    @command
    def getacl(self, path=None):
        path = format_path(self._cli.current_path, path)
        current_acl = self._zookeeper.get_acl(path)

        lines = []
        for i, acl in enumerate(current_acl):
            lines.append("{}: {} {} ({})".format(i,
                                                 acl.id.scheme,
                                                 acl.id.id,
                                                 ', '.join(acl.acl_list)))

        return "\n".join(lines)

    @command
    def addacl(self, permissions=None, path=None, scheme=None, id=None):
        if not path:
            raise CLIException("Missing node path")

        path = format_path(self._cli.current_path, path)
        self._zookeeper.add_acl(path, permissions, scheme, id)

        self._cli.log("Added ACL to {}: {}:{} ({})".format(path, scheme, id, permissions))

    @command
    def rmacl(self, path=None, index=None):
        if not path:
            raise CLIException("Missing node path")

        index = int(index)

        path = format_path(self._cli.current_path, path)
        deleted = self._zookeeper.delete_acl(path, index)

        self._cli.log("Deleted ACL from {}: {} {}".format(path, deleted.id.scheme, deleted.id.id))

    @command
    def help(self, parser, all_commands, subject):
        if subject:
            subparsers = [cmd for cmd in all_commands
                          if cmd.name == subject]
            if subparsers:
                parser = subparsers[0].parser

        return parser.print_help()

    @command
    def exit(self):
        self._cli.set_running(False)
