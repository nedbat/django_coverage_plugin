"""Base classes and helpers for testing the plugin."""

from __future__ import print_function, unicode_literals

import os
import os.path
import re

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

from django.template import Context, Template
from django.template.loader import get_template
from django.test import TestCase


class DjangoPluginTestCase(TempDirMixin, TestCase):
    """A base class for all our tests."""

    def path(self, name=None):
        return "templates/{}".format(name or self.template_file)

    def make_template(self, text, name=None):
        """Make a template with `text`.

        If `name` isn't provided, make a name from the test method name.
        The template is implicitly available for the other methods to use.

        """
        if name is not None:
            self.template_file = name
        else:
            self.template_file = self.id().rpartition(".")[2] + ".html"
        template_path = self.path(self.template_file)
        self.make_file(template_path, text)

    def run_django_coverage(
        self, name=None, text=None, context=None, options=None,
    ):
        """Run a template under coverage.

        The data context is `context` if provided, else {}.
        If `text` is provided, make a string template to run. Otherwise,
        if `name` is provided, run that template, otherwise use the last
        template made by `make_template`.

        If `options` is provided, they are kwargs for the Coverage
        constructor, which default to source=["."].

        Returns:
            str: the text produced by the template.

        """
        if options is None:
            options = {'source': ["."]}

        with self.settings(TEMPLATE_DIRS=("templates",)):
            if text is not None:
                tem = Template(text)
            else:
                tem = get_template(name or self.template_file)
            ctx = Context(context or {})
            # timid=True here temporarily just because the plugin code is in
            # pytracer.py, not in tracer.c yet.
            self.cov = coverage.Coverage(timid=True, **options)
            self.cov.config["run:plugins"].append("django_coverage_plugin")
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
        path = self.path(name)
        line_data = self.cov.data.line_data()[os.path.realpath(path)]
        return line_data

    def get_analysis(self, name=None):
        """Get the coverage analysis for a template.

        Returns:
            list, list: the line numbers of executable lines, and the line
                numbers of missed lines.

        """
        path = self.path(name)
        analysis = self.cov.analysis2(os.path.abspath(path))
        _, executable, _, missing, _ = analysis
        return executable, missing


def squashed(s):
    """Remove all of the whitespace from s."""
    return re.sub(r"\s", "", s)
