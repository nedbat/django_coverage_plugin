"""Test helpers for the django coverage plugin."""

import unittest

from django_coverage_plugin.plugin import make_line_map, get_line_number, dig


class HelperTest(unittest.TestCase):
    def test_line_maps(self):
        line_map = make_line_map("Hello\nWorld\n")
        # character positions:    012345 6789ab
        self.assertEqual(get_line_number(line_map, 0), 1)
        self.assertEqual(get_line_number(line_map, 1), 1)
        self.assertEqual(get_line_number(line_map, 5), 1)
        self.assertEqual(get_line_number(line_map, 6), 2)
        self.assertEqual(get_line_number(line_map, 7), 2)
        self.assertEqual(get_line_number(line_map, 11), 2)
        self.assertEqual(get_line_number(line_map, 12), -1)


class FakeFrame(object):
    def __init__(self, **kwargs):
        self.f_locals = kwargs


class Object(object):
    def __init__(self, **kwargs):
        self.__dict__ = kwargs


class DigTest(unittest.TestCase):
    def test_get_locals(self):
        frame = FakeFrame(a=17, b=23)
        self.assertEqual(dig(frame, ["a"], ["b"]), 17)
        self.assertEqual(dig(frame, ["x"], ["b"]), 23)
        self.assertEqual(dig(frame, ["x"], ["y"]), None)

    def test_get_deep(self):
        frame = FakeFrame(obj=Object(foo=[Object(bar=42)]))

        # We can get our value.
        self.assertEqual(dig(frame, ["obj", "foo", 0, "bar"]), 42)

        # The other options don't matter once we find what we need.
        self.assertEqual(dig(frame, ["obj", "foo", 0, "bar"], ["x"]), 42)

        # Near misses of various sorts are properly skipped, and we still get
        # what we need.
        good_path = ["obj", "foo", 0, "bar"]
        self.assertEqual(dig(frame, ["x"], good_path), 42)
        self.assertEqual(dig(frame, ["obj", "x"], good_path), 42)
        self.assertEqual(dig(frame, ["obj", "foo", "x"], good_path), 42)
        self.assertEqual(dig(frame, ["obj", "foo", 10], good_path), 42)
        self.assertEqual(dig(frame, ["obj", "foo", 0, "x"], good_path), 42)
