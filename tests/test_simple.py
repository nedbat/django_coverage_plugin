"""Simple tests for django_template_coverage."""

from __future__ import print_function, unicode_literals

import atexit
import os
import os.path

import coverage
from coverage.test_helpers import TempDirMixin

import django
from django.template import Context
from django.template.loader import get_template
from django.test import TestCase

# Make Django templates outside of Django: http://stackoverflow.com/a/98178/14343
from django.conf import settings
BOGUS_DB = '/tmp/django_coverage.db'
settings.configure(
    TEMPLATE_DEBUG = True,
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BOGUS_DB,
        }
    }
)
atexit.register(os.remove, BOGUS_DB)
django.setup()

# TODO: test what happens if TEMPLATE_DEBUG is not set.

class DjangoPluginTestCase(TempDirMixin, TestCase):
    def do_django_coverage(self, template, context={}):
        self.template_file = self.id().rpartition(".")[2] + ".html"
        self.template_path = "templates/{}".format(self.template_file)
        self.make_file(self.template_path, template)

        with self.settings(TEMPLATE_DIRS=("templates",)):
            tem = get_template(self.template_file)
            ctx = Context(context)
            # timid=True here just because the plugin code is in .py, not in .c yet.
            self.cov = coverage.Coverage(timid=True, source=["."])
            self.cov.config["run:plugins"].append("django_template_coverage")
            #cov.config["run:debug"].append("trace")
            self.cov.start()
            text = tem.render(ctx)
            self.cov.stop()
            self.cov.save()
            line_data = self.cov.data.line_data()[os.path.realpath(self.template_path)]
            return text, line_data

    def get_analysis(self, morf=None):
        if morf is None:
            morf = self.template_path
        filename, executable, excluded, missing, formatted = self.cov.analysis2(os.path.abspath(morf))
        return executable, missing, formatted


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
