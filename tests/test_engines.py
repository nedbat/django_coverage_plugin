# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""Tests of multiple engines for django_coverage_plugin."""

from django_coverage_plugin import DjangoTemplatePluginException

from .plugin_test import DjangoPluginTestCase, django_start_at


@django_start_at(1, 8)
class MultipleEngineTests(DjangoPluginTestCase):
    def setUp(self):
        super(MultipleEngineTests, self).setUp()

        # Move to module imports once we drop support for Django < 1.7
        from django.test import modify_settings
        engine = {
            'NAME': 'other',
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['templates2'],         # where the tests put things.
            'OPTIONS': {
                'debug': True,
            },
        }
        modified_settings = modify_settings(TEMPLATES={'append': [engine]})
        modified_settings.enable()
        self.addCleanup(modified_settings.disable)

        self.template_directory = 'templates2'

    def test_file_template(self):
        self.make_template('Hello')
        text = self.run_django_coverage(using='other')
        self.assertEqual(text, 'Hello')
        self.assert_analysis([1])

    def test_string_template(self):
        text = self.run_django_coverage(text='Hello', using='other')
        self.assertEqual(text, 'Hello')

    def test_third_engine_not_debug(self):
        from django.test import modify_settings
        engine3 = {
            'NAME': 'notdebug',
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['templates3'],         # where the tests put things.
        }
        modified_settings = modify_settings(TEMPLATES={'append': [engine3]})
        modified_settings.enable()
        self.addCleanup(modified_settings.disable)

        self.make_template('Hello')
        msg = "Template debugging must be enabled in settings."
        with self.assertRaisesRegexp(DjangoTemplatePluginException, msg):
            self.run_django_coverage()
