# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""Settings tests for django_coverage_plugin."""

import django
from django.test.utils import override_settings

from django_coverage_plugin import DjangoTemplatePluginException

from .plugin_test import DjangoPluginTestCase, test_settings, django_start_at


# Make settings overrides for tests below.
if django.VERSION >= (1, 8):
    NON_DJANGO_BACKEND = 'django.template.backends.dummy.TemplateStrings'

    DEBUG_FALSE_OVERRIDES = test_settings()
    DEBUG_FALSE_OVERRIDES['TEMPLATES'][0]['OPTIONS']['debug'] = False

    NO_OPTIONS_OVERRIDES = test_settings()
    del NO_OPTIONS_OVERRIDES['TEMPLATES'][0]['OPTIONS']

    OTHER_ENGINE_OVERRIDES = test_settings()
    OTHER_ENGINE_OVERRIDES['TEMPLATES'][0]['BACKEND'] = NON_DJANGO_BACKEND
    OTHER_ENGINE_OVERRIDES['TEMPLATES'][0]['OPTIONS'] = {}
else:
    DEBUG_FALSE_OVERRIDES = {'TEMPLATE_DEBUG': False}
    NO_OPTIONS_OVERRIDES = OTHER_ENGINE_OVERRIDES = {}


class SettingsTest(DjangoPluginTestCase):

    @override_settings(**DEBUG_FALSE_OVERRIDES)
    def test_debug_false(self):
        self.make_template('Hello')
        msg = "Template debugging must be enabled in settings."
        with self.assertRaisesRegexp(DjangoTemplatePluginException, msg):
            self.run_django_coverage()

    @django_start_at(1, 8)
    @override_settings(**NO_OPTIONS_OVERRIDES)
    def test_no_options(self):
        self.make_template('Hello')
        msg = "Template debugging must be enabled in settings."
        with self.assertRaisesRegexp(DjangoTemplatePluginException, msg):
            self.run_django_coverage()

    @django_start_at(1, 8)
    @override_settings(**OTHER_ENGINE_OVERRIDES)
    def test_other_engine(self):
        self.make_template('Hello')
        msg = "Can't use non-Django templates."
        with self.assertRaisesRegexp(DjangoTemplatePluginException, msg):
            self.run_django_coverage()
