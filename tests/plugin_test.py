"""Base classes and helpers for testing the plugin."""

from __future__ import print_function, unicode_literals

import os
import os.path

import coverage
from coverage.test_helpers import TempDirMixin

import django

# Make Django templates outside of Django.
# Originally taken from: http://stackoverflow.com/a/98178/14343
from django.conf import settings
settings.configure(
    CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
    },
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ":memory:",
        }
    },
    TEMPLATE_DEBUG=True,
)

if hasattr(django, "setup"):
    django.setup()

from django.template import Context
from django.template.loader import get_template
from django.test import TestCase


class DjangoPluginTestCase(TempDirMixin, TestCase):
    """A base class for all our tests."""

    def make_template(self, text, name=None):
        """Make a template with `text`.

        If `name` isn't provided, make a name from the test method name.
        The template is implicitly available for the other methods to use.

        """
        if name is not None:
            self.template_file = name
        else:
            self.template_file = self.id().rpartition(".")[2] + ".html"
        self.template_path = "templates/{}".format(self.template_file)
        self.make_file(self.template_path, text)

    def run_django_coverage(self, name=None, context=None):
        """Run a template under coverage.

        The data context is `context` if provided, else {}.
        If `name` is provided, run that template, otherwise use the last
        template made by `make_template`.

        Returns:
            str: the text produced by the template.

        """
        with self.settings(TEMPLATE_DIRS=("templates",)):
            tem = get_template(name or self.template_file)
            ctx = Context(context or {})
            # timid=True here temporarily just because the plugin code is in
            # pytracer.py, not in tracer.c yet.
            self.cov = coverage.Coverage(timid=True, source=["."])
            self.cov.config["run:plugins"].append("django_template_coverage")
            if 0:
                self.cov.config["run:debug"].append("trace")
            self.cov.start()
            text = tem.render(ctx)
            self.cov.stop()
            self.cov.save()
            return text

    def get_line_data(self, name=None):
        """Get the executed-line data for a template.

        Returns:
            list: the line numbers of lines executed in the template.

        """
        path = "templates/{}".format(name or self.template_file)
        line_data = self.cov.data.line_data()[os.path.realpath(path)]
        return line_data

    def get_analysis(self, name=None):
        """Get the coverage analysis for a template.

        Returns:
            list, list: the line numbers of executable lines, and the line
                numbers of missed lines.

        """
        if name is None:
            name = self.template_path
        analysis = self.cov.analysis2(os.path.abspath(name))
        _, executable, _, missing, _ = analysis
        return executable, missing
