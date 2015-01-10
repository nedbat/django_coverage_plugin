"""Tests of control-flow structures for django_template_coverage."""

from __future__ import print_function, unicode_literals

from .plugin_test import DjangoPluginTestCase


class ConditionalTest(DjangoPluginTestCase):

    def test_if(self):
        self.make_template("""\
            {% if foo %}
            Hello
            {% endif %}
            """)

        text = self.run_django_coverage(context={'foo': True})
        self.assertEqual(text.strip(), 'Hello')
        self.assertEqual(self.get_line_data(), [1, 2])

        text = self.run_django_coverage(context={'foo': False})
        self.assertEqual(text.strip(), '')
        self.assertEqual(self.get_line_data(), [1])
        self.assertEqual(self.get_analysis(), ([1, 2], [2]))

    def test_if_else(self):
        self.make_template("""\
            {% if foo %}
            Hello
            {% else %}
            Goodbye
            {% endif %}
            """)

        text = self.run_django_coverage(context={'foo': True})
        self.assertEqual(text.strip(), 'Hello')
        self.assertEqual(self.get_line_data(), [1, 2])
        self.assertEqual(self.get_analysis(), ([1, 2, 4], [4]))

        text = self.run_django_coverage(context={'foo': False})
        self.assertEqual(text.strip(), 'Goodbye')
        self.assertEqual(self.get_line_data(), [1, 4])
        self.assertEqual(self.get_analysis(), ([1, 2, 4], [2]))


class LoopTest(DjangoPluginTestCase):
    def test_loop(self):
        self.make_template("""\
            Before
            {% for item in items %}
            -{{ item }}
            {% endfor %}
            After
            """)

        text = self.run_django_coverage(context={'items': "ABC"})
        self.assertEqual(text, "Before\n\n-A\n\n-B\n\n-C\n\nAfter\n")
        self.assertEqual(self.get_line_data(), [1, 2, 3, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 5], []))

        text = self.run_django_coverage(context={'items': ""})
        self.assertEqual(text, "Before\n\nAfter\n")
        self.assertEqual(self.get_line_data(), [1, 2, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 5], [3]))

    def test_loop_with_empty_clause(self):
        self.make_template("""\
            Before
            {% for item in items %}
            -{{ item }}
            {% empty %}
            NONE
            {% endfor %}
            After
            """)

        text = self.run_django_coverage(context={'items': "ABC"})
        self.assertEqual(text, "Before\n\n-A\n\n-B\n\n-C\n\nAfter\n")
        self.assertEqual(self.get_line_data(), [1, 2, 3, 7])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 5, 7], [5]))

        text = self.run_django_coverage(context={'items': ""})
        self.assertEqual(text, "Before\n\nNONE\n\nAfter\n")
        self.assertEqual(self.get_line_data(), [1, 2, 5, 7])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 5, 7], [3]))
