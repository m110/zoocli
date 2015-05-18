#!/usr/bin/python3
import os
import sys
import unittest
from unittest.mock import patch
from kazoo.exceptions import NoNodeError

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from zoocli.config import load_config

load_config('../zoocli.example.conf')

from zoocli.cli import ZooCLI
from zoocli.exceptions import InvalidPath, MissingArgument


class CommandsTest(unittest.TestCase):
    def setUp(self):
        self.zookeeper_patcher = patch('zoocli.zookeeper.KazooClient')
        self.zookeeper = self.zookeeper_patcher.start()
        self.zookeeper.return_value = self.zookeeper

        self.cli = ZooCLI()
        self.cli._verbose = False

    def tearDown(self):
        self.zookeeper_patcher.stop()

    def test_ls(self):
        self.zookeeper.get_children.return_value = ['a', 'b', 'c']

        result = self.cli.execute('ls')
        self.assertEqual(result, "a b c")
        self.zookeeper.get_children.assert_called_once_with('/')

        result = self.cli.execute('ls', '-l')
        self.assertEqual(result, "a\nb\nc")

    def test_cd(self):
        self.zookeeper.get_children.return_value = []

        self.cli.execute('cd', '/any_node')
        self.assertEqual(self.cli.current_path, '/any_node')

        self.zookeeper.get_children.side_effect = NoNodeError
        with self.assertRaises(InvalidPath):
            self.cli.execute('cd', '/invalid_node')

    def test_get(self):
        self.zookeeper.get.return_value = (b"any_data", None)

        result = self.cli.execute('get', '/any_node')
        self.assertEqual(result, 'any_data')

    def test_set(self):
        with self.assertRaises(MissingArgument):
            self.cli.execute('set')

        with self.assertRaises(MissingArgument):
            self.cli.execute('set', '/any_node')

        self.cli.execute('set', '/any_node', 'any_data')
        self.zookeeper.set.assert_called_once_with('/any_node', b'any_data')

    def test_create(self):
        with self.assertRaises(MissingArgument):
            self.cli.execute('create')

        tests = [
            {'in': [],
             'expect': dict(value=b'', ephemeral=False, sequence=False, makepath=False),
             },
            {'in': ['any_data'],
             'expect': dict(value=b'any_data', ephemeral=False, sequence=False, makepath=False),
             },
            {'in': ['-e'],
             'expect': dict(value=b'', ephemeral=True, sequence=False, makepath=False),
             },
            {'in': ['-s'],
             'expect': dict(value=b'', ephemeral=False, sequence=True, makepath=False),
             },
            {'in': ['-p'],
             'expect': dict(value=b'', ephemeral=False, sequence=False, makepath=True),
             },
            {'in': ['any_data', '-ep'],
             'expect': dict(value=b'any_data', ephemeral=True, sequence=False, makepath=True),
             },
        ]

        for test in tests:
            self.zookeeper.create.reset_mock()
            self.cli.execute('create', '/any_node', *test['in'])
            self.zookeeper.create.assert_called_once_with('/any_node', **test['expect'])

    def test_rm(self):
        with self.assertRaises(MissingArgument):
            self.cli.execute('rm')

        self.zookeeper.delete.reset_mock()
        self.cli.execute('rm', '/any_path')
        self.zookeeper.delete.assert_called_once_with('/any_path', recursive=False)

        self.zookeeper.delete.reset_mock()
        self.cli.execute('rm', '/any_path', '-r')
        self.zookeeper.delete.assert_called_once_with('/any_path', recursive=True)

    def test_addacl(self):
        # TODO
        pass

    def test_rmacl(self):
        # TODO
        pass


if __name__ == "__main__":
    unittest.main()
