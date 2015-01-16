"""Tests of template inheritance for django_coverage_plugin."""

from __future__ import print_function, unicode_literals

from .plugin_test import DjangoPluginTestCase


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
        self.assertEqual(text, "PROLOG\nHello\n\nSECOND\n\nGoodbye\n")
        self.assertEqual(self.get_line_data("base.html"), [1, 2, 3])
        self.assertEqual(self.get_line_data("specific.html"), [1, 2, 5])
        self.assertEqual(self.get_analysis("base.html"), ([1, 2, 3], []))
        self.assertEqual(self.get_analysis("specific.html"), ([1, 2, 5], []))

    def test_inheriting_with_unused_blocks(self):
        self.make_template(name="base.html", text="""\
            Hello
            {% block second_line %}second{% endblock %}
            Goodbye
            """)

        self.make_template(name="specific.html", text="""\
            {% extends "base.html" %}

            {% block second_line %}
            SECOND
            {% endblock %}

            {% block sir_does_not_appear_in_this_movie %}
            I was bit by a moose once
            {% endblock %}
            """)

        text = self.run_django_coverage(name="specific.html")
        self.assertEqual(text, "Hello\n\nSECOND\n\nGoodbye\n")
        self.assertEqual(self.get_line_data("base.html"), [1, 2, 3])
        self.assertEqual(self.get_line_data("specific.html"), [1, 4])
        self.assertEqual(self.get_analysis("base.html"), ([1, 2, 3], []))
        self.assertEqual(self.get_analysis("specific.html"), ([1, 4, 8], [8]))
