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
    def do_django_coverage(self, template, context={}):
        self.template_file = self.id().rpartition(".")[2] + ".html"
        self.template_path = "templates/{}".format(self.template_file)
        self.make_file(self.template_path, template)

        with self.settings(TEMPLATE_DIRS=("templates",)):
            tem = get_template(self.template_file)
            ctx = Context(context)
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
            line_data = self.cov.data.line_data()[
                os.path.realpath(self.template_path)
            ]
            return text, line_data

    def get_analysis(self, morf=None):
        if morf is None:
            morf = self.template_path
        analysis = self.cov.analysis2(os.path.abspath(morf))
        _, executable, _, missing, formatted = analysis
        return executable, missing, formatted
