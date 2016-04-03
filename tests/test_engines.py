# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""Tests of multiple engines for django_coverage_plugin."""

from .plugin_test import DjangoPluginTestCase, django_start_at


@django_start_at(1, 8)
class MultipleEngineTests(DjangoPluginTestCase):
    @classmethod
    def setUpClass(cls):
        # Move to module imports once we drop support for Django < 1.7
        from django.test import modify_settings
        engine = {
            'NAME': 'other',
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['templates'],      # where the tests put things.
            'OPTIONS': {
                'debug': True,
            },
        }
        cls._modified_settings = modify_settings(TEMPLATES={'append': [engine]})
        cls._modified_settings.enable()

    @classmethod
    def tearDownClass(cls):
        cls._modified_settings.disable()

    def test_file_template(self):
        self.make_template('Hello')
        text = self.run_django_coverage(using='other')
        self.assertEqual(text, 'Hello')
        self.assert_analysis([1])

    def test_string_template(self):
        text = self.run_django_coverage(text='Hello', using='other')
        self.assertEqual(text, 'Hello')
