"""Settings tests for django_coverage_plugin."""

import copy

import django
from django.test import override_settings

from django_coverage_plugin import DjangoTemplatePluginException

from .plugin_test import DjangoPluginTestCase, test_settings


if django.VERSION >= (1, 8):
    DEBUG_FALSE_OVERRIDES = {
        'TEMPLATES': [copy.deepcopy(test_settings['TEMPLATES'][0])]
    }
    DEBUG_FALSE_OVERRIDES['TEMPLATES'][0]['OPTIONS']['debug'] = False
else:
    DEBUG_FALSE_OVERRIDES = {'TEMPLATE_DEBUG': False}


class SettingsTest(DjangoPluginTestCase):

    @override_settings(**DEBUG_FALSE_OVERRIDES)
    def test_debug_false(self):
        self.make_template('Hello')
        msg = "Template debugging must be enabled in settings."
        with self.assertRaisesRegexp(DjangoTemplatePluginException, msg):
            self.run_django_coverage()
