"""Simple tests for django_template_coverage."""

from __future__ import print_function, unicode_literals

from .plugin_test import DjangoPluginTestCase

# TODO: test what happens if TEMPLATE_DEBUG is not set.


class SimpleTemplateTest(DjangoPluginTestCase):
    def test_plain_text(self):
        text, line_data = self.do_django_coverage('Hello\nWorld\n')
        self.assertEqual(text, 'Hello\nWorld\n')
        self.assertEqual(line_data, [1, 2])

        self.assertEqual(self.get_analysis(), ([1, 2], [], ""))

    def test_if(self):
        template = """\
            {% if foo %}
            Hello
            {% endif %}
            """

        text, line_data = self.do_django_coverage(template, {'foo': True})
        self.assertEqual(text.strip(), 'Hello')
        self.assertEqual(line_data, [1, 2])

        text, line_data = self.do_django_coverage(template, {'foo': False})
        self.assertEqual(text.strip(), '')
        self.assertEqual(line_data, [1])

        self.assertEqual(self.get_analysis(), ([1, 2], [2], "2"))

    def test_if_else(self):
        template = """\
            {% if foo %}
            Hello
            {% else %}
            Goodbye
            {% endif %}
            """

        text, line_data = self.do_django_coverage(template, {'foo': True})
        self.assertEqual(text.strip(), 'Hello')
        self.assertEqual(line_data, [1, 2])

        self.assertEqual(self.get_analysis(), ([1, 2, 4], [4], "4"))

        text, line_data = self.do_django_coverage(template, {'foo': False})
        self.assertEqual(text.strip(), 'Goodbye')
        self.assertEqual(line_data, [1, 4])

        self.assertEqual(self.get_analysis(), ([1, 2, 4], [2], "2"))
