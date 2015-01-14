"""Tests of control-flow structures for django_template_coverage."""

from __future__ import print_function, unicode_literals

from .plugin_test import DjangoPluginTestCase, squashed


class IfTest(DjangoPluginTestCase):

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

    def test_if_elif_else(self):
        self.make_template("""\
            {% if foo %}
            Hello
            {% elif bar %}
            Aloha
            {% else %}
            Goodbye
            {% endif %}
            """)

        text = self.run_django_coverage(context={'foo': True, 'bar': False})
        self.assertEqual(text.strip(), 'Hello')
        self.assertEqual(self.get_line_data(), [1, 2])
        self.assertEqual(self.get_analysis(), ([1, 2, 4, 6], [4, 6]))

        text = self.run_django_coverage(context={'foo': False, 'bar': True})
        self.assertEqual(text.strip(), 'Aloha')
        self.assertEqual(self.get_line_data(), [1, 4])
        self.assertEqual(self.get_analysis(), ([1, 2, 4, 6], [2, 6]))

        text = self.run_django_coverage(context={'foo': False, 'bar': False})
        self.assertEqual(text.strip(), 'Goodbye')
        self.assertEqual(self.get_line_data(), [1, 6])
        self.assertEqual(self.get_analysis(), ([1, 2, 4, 6], [2, 4]))


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


class IfChangedTest(DjangoPluginTestCase):

    def test_ifchanged(self):
        self.make_template("""\
            {% for a,b in items %}
                {% ifchanged %}
                    {{ a }}
                {% endifchanged %}
                {{ b }}
            {% endfor %}
            """)

        text = self.run_django_coverage(context={
            'items': ["AX", "AY", "BZ", "BW"],
        })
        self.assertEqual(squashed(text), 'AXYBZW')
        self.assertEqual(self.get_line_data(), [1, 2, 3, 4, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 4, 5], []))

    def test_ifchanged_variable(self):
        self.make_template("""\
            {% for a,b in items %}
                {% ifchanged a %}
                    {{ a }}
                {% endifchanged %}
                {{ b }}
            {% endfor %}
            """)

        text = self.run_django_coverage(context={
            'items': ["AX", "AY", "BZ", "BW"],
        })
        self.assertEqual(squashed(text), 'AXYBZW')
        self.assertEqual(self.get_line_data(), [1, 2, 3, 4, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 4, 5], []))


class IfEqualTest(DjangoPluginTestCase):

    def test_ifequal(self):
        self.make_template("""\
            {% for i,x in items %}
                {% ifequal x "X" %}
                    X
                {% endifequal %}
                {{ i }}
            {% endfor %}
            """)

        text = self.run_django_coverage(context={
            'items': [(0, 'A'), (1, 'X'), (2, 'X'), (3, 'B')],
        })
        self.assertEqual(squashed(text), '0X1X23')
        self.assertEqual(self.get_line_data(), [1, 2, 3, 4, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 4, 5], []))

    def test_ifnotequal(self):
        self.make_template("""\
            {% for i,x in items %}
                {% ifnotequal x "X" %}
                    X
                {% endifnotequal %}
                {{ i }}
            {% endfor %}
            """)

        text = self.run_django_coverage(context={
            'items': [(0, 'A'), (1, 'X'), (2, 'X'), (3, 'B')],
        })
        self.assertEqual(squashed(text), 'X012X3')
        self.assertEqual(self.get_line_data(), [1, 2, 3, 4, 5])
        self.assertEqual(self.get_analysis(), ([1, 2, 3, 4, 5], []))
