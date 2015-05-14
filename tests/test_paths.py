#!/usr/bin/python3
import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from zoocli.paths import format_path, split_path


class PathsTest(unittest.TestCase):

    def test_format_path(self):
        tests = [
            ("/", "a", "/a"),
            ("/", "a/", "/a"),
            ("/", "   a/    ", "/a"),

            ("/a", "b", "/a/b"),
            ("/a", "b/c/d", "/a/b/c/d"),
            ("/a/b", "c/d", "/a/b/c/d"),

            ("/", "/a", "/a"),
            ("/a/b", "/c/d", "/c/d"),

            ("/", "./././", "/"),
            ("/", ".", "/"),

            ("/a", "..", "/"),
            ("/a/b", "..", "/a"),
            ("/a", "../b", "/b"),
            ("/a/b/c", "../..", "/a"),
            ("/a/b/c", "../../d", "/a/d"),
            ("/a/b/c", "../../..", "/"),
        ]

        for data in tests:
            current, path, expected = data

            result = format_path(current, path)
            if result != expected:
                self.fail("format_path('{}', '{}') == '{}' but expected '{}'".format(
                          current, path, result, expected))

        self.assertEqual(format_path('/a', ''), '/a')
        self.assertEqual(format_path('/a', '', default='/b'), '/b')

    def test_split_path(self):
        tests = [
            ("/", []),
            ("/a", ["a"]),
            ("/a/b/c/d", ["a", "b", "c", "d"]),
        ]

        for data in tests:
            path, expected = data
            self.assertEqual(split_path(path), expected)


if __name__ == "__main__":
    unittest.main()
