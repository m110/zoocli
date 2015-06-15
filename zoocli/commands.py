import os
import re
import atexit
import tempfile
from climb.commands import Commands, command, completers
from climb.exceptions import MissingArgument, CLIException
from climb.paths import ROOT_PATH, format_path
from climb.config import config

from zoocli.exceptions import ZooKeeperException
from zoocli.utils import timestamp_to_date
from zoocli.zookeeper import ZooKeeper


def using_path(required=False, default=None):
    def wrapper(function):
        def inner(self, path, **kwargs):
            if required and not path:
                raise MissingArgument("Missing node path")

            path = format_path(self._cli.current_path, path, default=default)
            return function(self, path, **kwargs)

        return inner
    return wrapper


class ZooCommands(Commands):

    def __init__(self, cli):
        super().__init__(cli)

        self._zookeeper = ZooKeeper(**config['zookeeper'])
        atexit.register(self._zookeeper.stop)

    @command
    @completers('path')
    @using_path()
    def ls(self, path=None, long=False):
        result = self._zookeeper.list(path)

        separator = "\n" if long else " "
        return separator.join(sorted(result))

    @command
    @completers('path')
    @using_path(default=ROOT_PATH)
    def cd(self, path=None):
        # No exception means correct path
        self._zookeeper.list(path)
        self._cli.set_current_path(path)

    @command
    @completers('path')
    @using_path()
    def get(self, path=None):
        data = self._zookeeper.get(path)
        return data

    @command
    @completers('path')
    @using_path(required=True)
    def set(self, path=None, data=None):
        if not data:
            raise MissingArgument("Missing data")

        self._zookeeper.set(path, data)
        self._cli.log("Set {} data: {}".format(path, data))

    @command
    @completers('path')
    @using_path()
    def editor(self, path):
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
    @completers('path')
    @using_path(required=True)
    def create(self, path=None, data=None, ephemeral=False, sequence=False, makepath=False):
        self._zookeeper.create(path, data, ephemeral, sequence, makepath)
        self._cli.log("Created: {}".format(path))

    @command
    @completers('path')
    @using_path(required=True)
    def rm(self, path=None, recursive=False):
        self._zookeeper.delete(path, recursive)
        self._cli.log("Removed: {}".format(path))

    @command
    @completers('path')
    @using_path()
    def stat(self, path=None):
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
    @completers('path')
    @using_path()
    def getacl(self, path=None):
        current_acl = self._zookeeper.get_acl(path)

        lines = []
        for i, acl in enumerate(current_acl):
            lines.append("{}: {} {} ({})".format(i,
                                                 acl.id.scheme,
                                                 acl.id.id,
                                                 ', '.join(acl.acl_list)))

        return "\n".join(lines)

    @command
    @completers('path')
    @using_path(required=True)
    def addacl(self, permissions=None, path=None, scheme=None, id=None):
        self._zookeeper.add_acl(path, permissions, scheme, id)

        self._cli.log("Added ACL to {}: {}:{} ({})".format(path, scheme, id, permissions))

    @command
    @completers('path')
    @using_path(required=True)
    def rmacl(self, path=None, index=None):
        index = int(index)

        deleted = self._zookeeper.delete_acl(path, index)

        self._cli.log("Deleted ACL from {}: {} {}".format(path, deleted.id.scheme, deleted.id.id))

    @command
    @completers('path')
    @using_path()
    def find(self, path=None, name_filter=None, mindepth=None, maxdepth=None):
        def filter_depth(depth):
            if depth is None:
                return None

            try:
                depth = int(depth)
            except ValueError:
                raise CLIException("Depth has to be an integer")

            if depth < 0:
                raise CLIException("Depth can't be negative")

            return depth

        def filter_matches(name):
            return not name_filter or re.search(r"^{}$".format(name_filter), name)

        def list_deep(root, depth):
            if maxdepth is not None and depth > maxdepth:
                return []

            try:
                child_list = self._zookeeper.list(root)
            except ZooKeeperException as exc:
                print(exc)
                return []

            subnodes = []
            for child in child_list:
                child_path = os.path.join(root, child)

                if mindepth is None or depth >= mindepth:
                    if filter_matches(child):
                        subnodes.append(child_path)

                subnodes.extend(list_deep(child_path, depth + 1))

            return subnodes

        mindepth = filter_depth(mindepth)
        maxdepth = filter_depth(maxdepth)

        result = []
        if mindepth is None or mindepth == 0:
            name = path.split('/')[-1]
            if filter_matches(name):
                result.append(path)

        result.extend(list_deep(path, 1))

        return "\n".join(result)
