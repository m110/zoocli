from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError, NodeExistsError, NotEmptyError, InvalidACLError
from kazoo.security import make_acl, make_digest_acl

from zoocli.exceptions import InvalidPath

PERMS_MAP = {
    'a': 'admin',
    'c': 'create',
    'd': 'delete',
    'r': 'read',
    'w': 'write',
}

def get_permissions(permissions):
    return {PERMS_MAP[perm]: True for perm in permissions}


class ZooKeeper(object):

    def __init__(self, hosts, user=None, password=None):
        self._zookeeper = KazooClient(hosts=hosts)
        self._zookeeper.start()

        if user and password:
            self._zookeeper.add_auth('digest', '{}:{}'.format(user, password))

    def stop(self):
        if self._zookeeper:
            self._zookeeper.stop()
            self._zookeeper.close()
            self._zookeeper = None

    def list(self, path):
        try:
            return self._zookeeper.get_children(path)
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))

    def get(self, path):
        try:
            value, _ = self._zookeeper.get(path)
            if value:
                value = value.decode('utf-8')
            else:
                value = ""

            return value
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))

    def set(self, path, data):
        try:
            self._zookeeper.set(path, data.encode())
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))

    def create(self, path, data=None, ephemeral=False, sequence=False, makepath=False):
        if data:
            data = data.encode()
        else:
            data = b""

        try:
            self._zookeeper.create(path,
                                   value=data,
                                   ephemeral=ephemeral,
                                   sequence=sequence,
                                   makepath=makepath)
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))
        except NodeExistsError:
            raise InvalidPath("Node already exists: {}".format(path))

    def delete(self, path, recursive=False):
        try:
            self._zookeeper.delete(path, recursive=recursive)
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))
        except NotEmptyError:
            raise InvalidPath("Node contains sub-nodes")

    def stat(self, path):
        try:
            _, stat = self._zookeeper.get(path)
            return stat
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))

    def get_acl(self, path):
        try:
            acl, _ = self._zookeeper.get_acls(path)
            return acl
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))

    def add_acl(self, path, permissions, scheme, id):
        perms = get_permissions(permissions)

        if scheme == "digest":
            username, password = id.split(":")
            acl = make_digest_acl(username, password, **perms)
        else:
            acl = make_acl(scheme, id, **perms)

        current_acls = self.get_acl(path)
        current_acls.append(acl)

        try:
            self._zookeeper.set_acls(path, current_acls)
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))
        except InvalidACLError as exc:
            raise InvalidPath("Invalid ACL format: {}".format(str(exc)))

    def delete_acl(self, path, index):
        current_acls = self.get_acl(path)
        deleted = current_acls.pop(index)

        try:
            self._zookeeper.set_acls(path, current_acls)
        except NoNodeError:
            raise InvalidPath("No such node: {}".format(path))

        return deleted
