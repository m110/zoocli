from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

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
