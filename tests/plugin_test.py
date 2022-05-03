# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""Base classes and helpers for testing the plugin."""

import contextlib
import os
import os.path
import re
import unittest

import coverage
import django
from django.conf import settings
from django.template import Context, Template  # noqa
from django.template.backends.django import DjangoTemplates  # noqa
from django.template.loader import get_template  # noqa
from django.test import TestCase  # noqa
from unittest_mixins import StdStreamCapturingMixin, TempDirMixin

from django_coverage_plugin.plugin import DjangoTemplatePlugin


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

    the_settings.update({
        'TEMPLATES': [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': ['templates'],      # where the tests put things.
                'OPTIONS': {
                    'debug': True,
                    'loaders': [
                        'django.template.loaders.filesystem.Loader',
                    ]
                },
            },
        ],
    })

    if django.VERSION < (1, 10):
        # for {% ssi %}
        the_settings['TEMPLATES'][0]['OPTIONS']['allowed_include_roots'] = [""]

    return the_settings


settings.configure(**test_settings())

if hasattr(django, "setup"):
    django.setup()


class DjangoPluginTestCase(StdStreamCapturingMixin, TempDirMixin, TestCase):
    """A base class for all our tests."""

    def setUp(self):
        super(DjangoPluginTestCase, self).setUp()
        self.template_directory = "templates"

    def _path(self, name=None):
        return "{}/{}".format(self.template_directory, name or self.template_file)

    def make_template(self, text, name=None):
        """Make a template with `text`.

        If `name` isn't provided, make a name from the test method name.
        The template is implicitly available for the other methods to use.

        """
        if name is not None:
            self.template_file = name
        else:
            self.template_file = self.id().rpartition(".")[2] + ".html"
        template_path = self._path(self.template_file)
        return os.path.abspath(self.make_file(template_path, text))

    def run_django_coverage(
        self, name=None, text=None, context=None, options=None, using=None
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
        use_real_context = False

        if options is None:
            options = {'source': ["."]}

        if using:
            from django.template import engines
            engine = engines[using]
            if text is not None:
                tem = engine.from_string(text)
            else:
                tem = engine.get_template(name or self.template_file)
        elif text is not None:
            tem = Template(text)
            use_real_context = True
        else:
            tem = get_template(name or self.template_file)

        ctx = context or {}
        if use_real_context:
            # Before 1.8, render() wanted a Context. After, it wants a dict.
            ctx = Context(ctx)

        self.cov = coverage.Coverage(**options)
        self.append_config("run:plugins", "django_coverage_plugin")
        if 0:
            self.append_config("run:debug", "trace")
        self.cov.start()
        text = tem.render(ctx)
        self.cov.stop()
        self.cov.save()
        # Warning! Accessing secret internals!
        if hasattr(self.cov, 'plugins'):
            plugins = self.cov.plugins
        else:
            plugins = self.cov._plugins
        for pl in plugins:
            if isinstance(pl, DjangoTemplatePlugin):
                if not pl._coverage_enabled:
                    raise PluginDisabled()
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
        path = self._path(name)
        line_data = self.cov.data.line_data()[os.path.realpath(path)]
        return line_data

    def get_analysis(self, name=None):
        """Get the coverage analysis for a template.

        Returns:
            list, list: the line numbers of executable lines, and the line
                numbers of missed lines.

        """
        path = self._path(name)
        analysis = self.cov.analysis2(os.path.abspath(path))
        _, executable, _, missing, _ = analysis
        return executable, missing

    def assert_measured_files(self, *template_files):
        """Assert that the measured files are `template_files`.

        The names in `template_files` are the base names of files
        in the templates directory.
        """
        measured = {os.path.relpath(f) for f in self.cov.get_data().measured_files()}
        expected = {os.path.join("templates", f) for f in template_files}
        self.assertEqual(measured, expected)

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
        path = self._path(name)
        html_coverage = self.cov.html_report(os.path.abspath(path))
        return html_coverage

    def get_xml_report(self, name=None):
        """Get the xml report for a template.

        Returns:
            float: the total percentage covered.

        """
        path = self._path(name)
        xml_coverage = self.cov.xml_report(os.path.abspath(path))
        return xml_coverage

    @contextlib.contextmanager
    def assert_plugin_disabled(self, msg):
        """Assert that our plugin was disabled during an operation."""
        # self.run_django_coverage will raise PluginDisabled if the plugin
        # was disabled.
        # Coverage.py 6.0 made the warnings real warnings, so we have to adapt
        # how we test the warnings based on the version.
        if coverage.version.version_info >= (6, 0):
            import coverage.exceptions as cov_exc
            ctxmgr = self.assertWarns(cov_exc.CoverageWarning)
        else:
            ctxmgr = nullcontext()
        with ctxmgr as cw:
            with self.assertRaises(PluginDisabled):
                yield

        if cw is not None:
            warn_text = "\n".join(str(w.message) for w in cw.warnings)
        else:
            warn_text = self.stderr()
        self.assertIn(
            "Disabling plug-in 'django_coverage_plugin.DjangoTemplatePlugin' "
            "due to an exception:",
            warn_text
        )
        self.assertIn("DjangoTemplatePluginException: " + msg, warn_text)


def squashed(s):
    """Remove all of the whitespace from s."""
    return re.sub(r"\s", "", s)


def django_start_at(*needed_version):
    """A decorator for tests to require a minimum version of Django.

    @django_start_at(1, 10)      # Don't run the test on 1.10 or lower.
    def test_thing(self):
        ...

    """
    if django.VERSION >= needed_version:
        return lambda func: func
    else:
        return unittest.skip("Django version must be newer")


def django_stop_before(*needed_version):
    """A decorator for tests to require a maximum version of Django.

    @django_stop_before(1, 10)       # Don't run the test on 1.10 or higher.
    def test_thing(self):
        ...

    """
    if django.VERSION < needed_version:
        return lambda func: func
    else:
        return unittest.skip("Django version must be older")


class PluginDisabled(Exception):
    """Raised if we find that our plugin has been disabled."""
    pass


@contextlib.contextmanager
def nullcontext():
    """For when we need a context manager to do nothing."""
    yield None
