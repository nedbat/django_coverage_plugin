# coding: utf8
"""Simple tests for django_coverage_plugin."""

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

    def test_variable(self):
        self.make_template("""\
            Hello, {{name}}
            """)
        text = self.run_django_coverage(context={'name': 'John'})
        self.assertEqual(text, "Hello, John\n")
        self.assertEqual(self.get_line_data(), [1])
        self.assertEqual(self.get_analysis(), ([1], []))

    def test_variable_on_second_line(self):
        self.make_template("""\
            Hello,
            {{name}}
            """)
        text = self.run_django_coverage(context={'name': 'John'})
        self.assertEqual(text, "Hello,\nJohn\n")
        self.assertEqual(self.get_line_data(), [1, 2])
        self.assertEqual(self.get_analysis(), ([1, 2], []))

    def test_lone_variable(self):
        self.make_template("""\
            {{name}}
            """)
        text = self.run_django_coverage(context={'name': 'John'})
        self.assertEqual(text, "John\n")
        self.assertEqual(self.get_line_data(), [1])
        self.assertEqual(self.get_analysis(), ([1], []))

    def test_long_text(self):
        self.make_template("line\n"*50)
        text = self.run_django_coverage()
        self.assertEqual(text, "line\n"*50)
        self.assertEqual(self.get_line_data(), list(range(1, 51)))
        self.assertEqual(self.get_analysis(), (list(range(1, 51)), []))

    def test_non_ascii(self):
        self.make_template("""\
            υηιcσɗє ιѕ тяιcку
            {{more}}!
            """)
        text = self.run_django_coverage(context={'more': u'ɘboɔinU'})
        self.assertEqual(text, u'υηιcσɗє ιѕ тяιcку\nɘboɔinU!\n')
        self.assertEqual(self.get_line_data(), [1, 2])
        self.assertEqual(self.get_analysis(), ([1, 2], []))
        self.assertEqual(self.get_html_report(), 100)
        self.assertEqual(self.get_xml_report(), 100)


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
        self.assertEqual(self.get_html_report(), 100)
        self.assertEqual(self.get_xml_report(), 100)

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
        self.assertEqual(self.get_html_report(), 100)
        self.assertEqual(self.get_xml_report(), 100)

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
        self.assertEqual(self.get_html_report(), 100)
        self.assertEqual(self.get_xml_report(), 100)


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
        self.assertEqual(self.get_html_report(), 100)
        self.assertEqual(self.get_xml_report(), 100)


class StringTemplateTest(DjangoPluginTestCase):

    run_in_temp_dir = False

    def test_string_template(self):
        text = self.run_django_coverage(
            text="Hello, {{name}}!",
            context={'name': 'World'},
            options={},
            )
        self.assertEqual(text, "Hello, World!")


class BranchTest(DjangoPluginTestCase):

    def test_with_branch_enabled(self):
        self.make_template('Hello\nWorld\n\nGoodbye')
        text = self.run_django_coverage(
            options={'source': ["."], 'branch': True}
            )
        self.assertEqual(text, 'Hello\nWorld\n\nGoodbye')
        self.assertEqual(self.get_line_data(), [1, 2, 3, 4])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 4], []))
        self.assertEqual(self.get_html_report(), 100)
        self.assertEqual(self.get_xml_report(), 100)
