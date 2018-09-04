# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""Settings tests for django_coverage_plugin."""

from django.test.utils import override_settings

from .plugin_test import DjangoPluginTestCase, test_settings

# Make settings overrides for tests below.
NON_DJANGO_BACKEND = 'django.template.backends.dummy.TemplateStrings'

DEBUG_FALSE_OVERRIDES = test_settings()
DEBUG_FALSE_OVERRIDES['TEMPLATES'][0]['OPTIONS']['debug'] = False

NO_OPTIONS_OVERRIDES = test_settings()
del NO_OPTIONS_OVERRIDES['TEMPLATES'][0]['OPTIONS']

OTHER_ENGINE_OVERRIDES = test_settings()
OTHER_ENGINE_OVERRIDES['TEMPLATES'][0]['BACKEND'] = NON_DJANGO_BACKEND
OTHER_ENGINE_OVERRIDES['TEMPLATES'][0]['OPTIONS'] = {}


class SettingsTest(DjangoPluginTestCase):
    """Tests of detecting that the settings need to be right for the plugin to work."""

    @override_settings(**DEBUG_FALSE_OVERRIDES)
    def test_debug_false(self):
        self.make_template('Hello')
        with self.assert_plugin_disabled("Template debugging must be enabled in settings."):
            self.run_django_coverage()

    @override_settings(**NO_OPTIONS_OVERRIDES)
    def test_no_options(self):
        self.make_template('Hello')
        with self.assert_plugin_disabled("Template debugging must be enabled in settings."):
            self.run_django_coverage()

    @override_settings(**OTHER_ENGINE_OVERRIDES)
    def test_other_engine(self):
        self.make_template('Hello')
        with self.assert_plugin_disabled("Can't use non-Django templates."):
            self.run_django_coverage()
