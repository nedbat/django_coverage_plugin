"""Simple tests for django_template_coverage."""

from __future__ import print_function, unicode_literals

from .plugin_test import DjangoPluginTestCase

# TODO: test what happens if TEMPLATE_DEBUG is not set.


class SimpleTemplateTest(DjangoPluginTestCase):

    def test_one_line(self):
        self.make_template('Hello')
        text = self.run_django_coverage()
        self.assertEqual(text, 'Hello')
        self.assertEqual(self.get_line_data(), [1])
        self.assertEqual(self.get_analysis(), ([1], []))

    def test_plain_text(self):
        self.make_template('Hello\nWorld\n\nGoodbye')
        text = self.run_django_coverage()
        self.assertEqual(text, 'Hello\nWorld\n\nGoodbye')
        self.assertEqual(self.get_line_data(), [1, 2, 3, 4])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 4], []))


class CommentTest(DjangoPluginTestCase):

    def test_simple(self):
        self.make_template("""\
            First
            {% comment %}
                ignore this
            {% endcomment %}
            Last
            """)
        text = self.run_django_coverage()
        self.assertEqual(text, "First\n\nLast\n")
        self.assertEqual(self.get_line_data(), [1, 2, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 5], []))

    def test_with_stuff_inside(self):
        self.make_template("""\
            First
            {% comment %}
                {% if foo %}
                    {{ foo }}
                {% endif %}
            {% endcomment %}
            Last
            """)
        text = self.run_django_coverage()
        self.assertEqual(text, "First\n\nLast\n")
        self.assertEqual(self.get_line_data(), [1, 2, 7])
        self.assertEqual(self.get_analysis(), ([1, 2, 7], []))

    def test_inline_comment(self):
        self.make_template("""\
            First
            {# disregard all of this #}
            Last
            """)
        text = self.run_django_coverage()
        self.assertEqual(text, "First\n\nLast\n")
        self.assertEqual(self.get_line_data(), [1, 3])
        self.assertEqual(self.get_analysis(), ([1, 3], []))


class OtherTest(DjangoPluginTestCase):

    def test_filter(self):
        self.make_template("""\
            First
            {% filter force_escape|lower %}
                LOOK: 1 < 2
            {% endfilter %}
            Last
            """)
        text = self.run_django_coverage()
        self.assertEqual(text, "First\n\n    look: 1 &lt; 2\n\nLast\n")
        self.assertEqual(self.get_line_data(), [1, 2, 3, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 5], []))
