from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError, NodeExistsError, NotEmptyError

from zoocli.config import config
from zoocli.exceptions import InvalidPath


class ZooKeeper(object):

    def __init__(self):
        self._zookeeper = KazooClient(hosts=config['zookeeper']['hosts'])
        self._zookeeper.start()

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
            return value.decode('utf-8')
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
