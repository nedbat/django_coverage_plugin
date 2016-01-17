# coding: utf8
# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""Tests of HTML reporting for django_coverage_plugin."""

from .plugin_test import DjangoPluginTestCase


class HtmlTest(DjangoPluginTestCase):

    def test_simple(self):
        self.make_template("""\
            Simple © 2015
            """)

        self.run_django_coverage()
        self.cov.html_report()
        with open("htmlcov/templates_test_simple_html.html") as fhtml:
            html = fhtml.read()
        self.assertIn('<span class="txt">Simple &#169; 2015</span>', html)
