# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""Tests of template inheritance for django_coverage_plugin."""

from .plugin_test import DjangoPluginTestCase


class FindSourceTest(DjangoPluginTestCase):

    def test_finding_source(self):
        # This is a template that is rendered.
        self.make_template(name="main.html", text="Hello")
        # These are templates that aren't rendered, but are considered renderable.
        self.make_template(name="unused.html", text="Not used")
        self.make_template(name="unused.htm", text="Not used")
        self.make_template(name="unused.txt", text="Not used")
        # These are things left behind by an editor.
        self.make_template(name="~unused.html", text="junk")
        self.make_template(name="unused=.html", text="junk")
        self.make_template(name="unused.html,", text="junk")
        # This is some other file format we don't recognize.
        self.make_template(name="phd.tex", text="Too complicated to read")

        text = self.run_django_coverage(name="main.html")
        self.assertEqual(text, "Hello")

        # The rendered file has data, and was measured.
        self.assert_analysis([1], name="main.html")
        # The unrendered files have data, and were not measured.
        self.assert_analysis([1], name="unused.html", missing=[1])
        self.assert_analysis([1], name="unused.htm", missing=[1])
        self.assert_analysis([1], name="unused.txt", missing=[1])
        # The editor leave-behinds are not in the measured files.
        self.assert_measured_files("main.html", "unused.html", "unused.htm", "unused.txt")

    def test_customized_extensions(self):
        self.make_file(".coveragerc", """\
            [run]
            plugins = django_coverage_plugin
            [django_coverage_plugin]
            template_extensions = html, tex
            """)
        # This is a template that is rendered.
        self.make_template(name="main.html", text="Hello")
        # These are templates that aren't rendered, but are considered renderable.
        self.make_template(name="unused.html", text="Not used")
        self.make_template(name="phd.tex", text="Too complicated to read")
        # These are things left behind by an editor.
        self.make_template(name="~unused.html", text="junk")
        self.make_template(name="unused=.html", text="junk")
        self.make_template(name="unused.html,", text="junk")
        # This is some other file format we don't recognize.
        self.make_template(name="unused.htm", text="Not used")
        self.make_template(name="unused.txt", text="Not used")

        text = self.run_django_coverage(name="main.html")
        self.assertEqual(text, "Hello")

        # The rendered file has data, and was measured.
        self.assert_analysis([1], name="main.html")
        # The unrendered files have data, and were not measured.
        self.assert_analysis([1], name="unused.html", missing=[1])
        self.assert_analysis([1], name="phd.tex", missing=[1])
        # The editor leave-behinds are not in the measured files.
        self.assert_measured_files("main.html", "unused.html", "phd.tex")
