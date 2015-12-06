"""Base classes and helpers for testing the plugin."""

import os
import os.path
import re
import unittest

import coverage
from coverage.test_helpers import TempDirMixin

import django
from django.conf import settings


def test_settings():
    """Create a dict full of default Django settings for the tests."""
    the_settings = {
        'CACHES': {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            },
        },
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        'ROOT_URLCONF': 'tests',
    }

    if django.VERSION >= (1, 8):
        the_settings.update({
            'TEMPLATES': [
                {
                    'BACKEND': 'django.template.backends.django.DjangoTemplates',
                    'DIRS': ['templates'],      # where the tests put things.
                    'OPTIONS': {
                        'debug': True,
                    },
                },
            ],
        })

        if django.VERSION < (1, 10):
            # for {% ssi %}
            the_settings['TEMPLATES'][0]['OPTIONS']['allowed_include_roots'] = ['/']

    else:
        the_settings.update({
            'ALLOWED_INCLUDE_ROOTS': ['/'],     # for {% ssi %}
            'TEMPLATE_DEBUG': True,
            'TEMPLATE_DIRS': ['templates'],     # where the tests put things.
        })

    return the_settings

settings.configure(**test_settings())

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
        return os.path.abspath(self.make_file(template_path, text))

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

        with self.settings():
            if text is not None:
                tem = Template(text)
            else:
                tem = get_template(name or self.template_file)
            ctx = Context(context or {})
            self.cov = coverage.Coverage(**options)
            self.append_config("run:plugins", "django_coverage_plugin")
            if 0:
                self.append_config("run:debug", "trace")
            self.cov.start()
            text = tem.render(ctx)
            self.cov.stop()
            self.cov.save()
            return text

    def append_config(self, option, value):
        """Append to a configuration option."""
        val = self.cov.config.get_option(option)
        val.append(value)
        self.cov.config.set_option(option, val)

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

    def measured_files(self):
        """Get the list of measured files, in relative form."""
        return [os.path.relpath(f) for f in self.cov.data.measured_files()]

    def assert_analysis(self, executable, missing=None, name=None):
        """Assert that the analysis for `name` is right."""
        actual_executable, actual_missing = self.get_analysis(name)
        self.assertEqual(
            executable,
            actual_executable,
            "Executable lines aren't as expected: %r != %r" % (
                executable, actual_executable,
            ),
        )
        self.assertEqual(
            missing or [],
            actual_missing,
            "Missing lines aren't as expected: %r != %r" % (
                missing, actual_missing,
            ),
        )

    def get_html_report(self, name=None):
        """Get the html report for a template.

        Returns:
            float: the total percentage covered.

        """
        path = self.path(name)
        html_coverage = self.cov.html_report(os.path.abspath(path))
        return html_coverage

    def get_xml_report(self, name=None):
        """Get the xml report for a template.

        Returns:
            float: the total percentage covered.

        """
        path = self.path(name)
        xml_coverage = self.cov.xml_report(os.path.abspath(path))
        return xml_coverage


def squashed(s):
    """Remove all of the whitespace from s."""
    return re.sub(r"\s", "", s)


def django_start_at(*needed_version):
    """A decorator for tests to require a minimum version of Django.

    @django_start_at(1, 8)      # Don't run the test on 1.7 or lower.
    def test_thing(self):
        ...

    """
    if django.VERSION >= needed_version:
        return lambda func: func
    else:
        return unittest.skip("Django version must be newer")


def django_stop_at(*needed_version):
    """A decorator for tests to require a maximum version of Django.

    @django_stop_at(1, 8)       # Don't run the test on 1.8 or higher.
    def test_thing(self):
        ...

    """
    if django.VERSION < needed_version:
        return lambda func: func
    else:
        return unittest.skip("Django version must be older")
