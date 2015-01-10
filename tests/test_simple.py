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


class BlockTest(DjangoPluginTestCase):

    def test_empty_block(self):
        self.make_template("""\
            {% block somewhere %}{% endblock %}
            """)

        text = self.run_django_coverage()
        self.assertEqual(text.strip(), '')
        self.assertEqual(self.get_line_data(), [1])
        self.assertEqual(self.get_analysis(), ([1], []))

    def test_empty_block_with_text_inside(self):
        self.make_template("""\
            {% block somewhere %}Hello{% endblock %}
            """)

        text = self.run_django_coverage()
        self.assertEqual(text.strip(), 'Hello')
        self.assertEqual(self.get_line_data(), [1])
        self.assertEqual(self.get_analysis(), ([1], []))

    def test_empty_block_with_text_outside(self):
        self.make_template("""\
            {% block somewhere %}{% endblock %}
            Hello
            """)

        text = self.run_django_coverage()
        self.assertEqual(text.strip(), 'Hello')
        self.assertEqual(self.get_line_data(), [1, 2])
        self.assertEqual(self.get_analysis(), ([1, 2], []))

    def test_two_empty_blocks(self):
        self.make_template("""\
            {% block somewhere %}{% endblock %}
            X
            {% block elsewhere %}{% endblock %}
            Y
            """)

        text = self.run_django_coverage()
        self.assertEqual(text.strip(), 'X\n\nY')
        self.assertEqual(self.get_line_data(), [1, 2, 3, 4])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 4], []))

    def test_inheriting(self):
        self.make_template(name="base.html", text="""\
            Hello
            {% block second_line %}second{% endblock %}
            Goodbye
            """)

        self.make_template(name="specific.html", text="""\
            PROLOG
            {% extends "base.html" %}
            THIS DOESN'T APPEAR
            {% block second_line %}
            SECOND
            {% endblock %}

            THIS WON'T EITHER
            """)

        text = self.run_django_coverage(name="specific.html")
        self.assertEqual(text.strip(), "PROLOG\nHello\n\nSECOND\n\nGoodbye")
        self.assertEqual(self.get_line_data("base.html"), [1, 2, 3])
        self.assertEqual(self.get_line_data("specific.html"), [1, 2, 5])
        self.assertEqual(self.get_analysis("base.html"), ([1, 2, 3], []))
        self.assertEqual(self.get_analysis("specific.html"), ([1, 2, 5], []))
