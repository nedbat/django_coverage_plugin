# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""
    Full integration tests for django_coverage_plugin.
    The tests in this module instantiate a minimal but complete
    Django project and run tests against it.  This allows for
    testing against various startup conditions since in other tests,
    the django startup procedure is only executes once for each
    python/django version combination.
"""

import os
import shutil
import subprocess

from .plugin_test import DjangoPluginTestCase

import django

VIEW_FUNC_TEXT = """
def target_view(request):
    return render(
        request,
        "target_template.html",
        {"varA": 1212, "varB": "DcDc"},
    )
"""

TEMPLATE_FILE_TEXT = """
{% load test_tags %}

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Example: {{ varA }}</title>
</head>
<body>
{% if varA %}
    {{ varA }}
{% endif %}
<br/>
{% if varA %}
    {{ varB }}
{% endif %}
LOWER: {{ varB|lower }}
</body>
</html>
"""
COVERAGE_CFG_FILE_TEXT = """
[run]
plugins =
    django_coverage_plugin

omit = .tox

[report]
ignore_errors = True

[combine]
ignore_errors = True
"""

TEST_VIEWS_FILE_TEXT = """
import django
from django.test import TestCase

class TestViews(TestCase):
   def test_view_target_view(self):
        %(import_reverse)s

        %(define_target_view)s

        resp = self.client.get(reverse(target_view))
        self.assertContains(resp, '1212')
        self.assertContains(resp, 'DcDc')
        self.assertContains(resp, 'LOWER: dcdc')
        self.assertContains(resp, '<title>Example: 1212</title>')

"""
TEMPLATE_TAG_TEXT = """
from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(is_safe=True)
@stringfilter
def lower(value):
    return mark_safe(value.lower())

"""


def change_elem(data, elem_name, sep, func):
    """
    Find the configuration definition in `data`, evaluate
    that defnition, pass the value to func, and convert the output
    into the expected text format.

    :param data:  Block of text
    :param elem_name:  Name of element to be changed.  Must be defined
    at the first column of the data text
    :param sep:  separator to use in the definition
    :param func: function to be called for transformation
    :return: updated data text
    """
    sep_open, sep_close = {"]": ("[", "]"), ")": ("(", ")")}[sep]
    before, after = data.split("%s = %s" % (elem_name, sep_open), 1)

    # Find the end of the value definition, note that the closing
    # separator must always be on its own line
    middle, after = after.split("\n%s\n" % sep_close, 1)

    # Put the separators back
    elem = "%s%s%s" % (sep_open, middle, sep_close)

    # Use eval to convert the text of value into a python data object
    elem = eval(elem)

    # Call func to transform the python data object
    elem = func(elem)

    # use pprint to convert the data to text and put it all back together
    import pprint
    middle = pprint.pformat(elem)
    middle = "%s\n%s\n" % (middle[:-1], sep)
    data = "%s%s = %s%s" % (before, elem_name, middle, after)
    return data


class IntegrationTest(DjangoPluginTestCase):
    """Tests greenfield settings initializations and other weirdnesses"""

    def setUp(self):
        self.python = ""

        if '_' in os.environ:
            self.python = os.path.abspath(os.environ['_'])
        elif "VIRTUAL_ENV" in os.environ:
            self.python = "%s/bin/python" % os.environ["VIRTUAL_ENV"]

        if ".tox" in self.python:
            self.env_bin = os.path.dirname(self.python)
        else:
            self.env_bin = ""
            self.python = ""

    def set_cwd(self, path):
        self.cwd = path

    def _cmd(self, *args, **kwargs):
        try:
            output = subprocess.check_output(args, cwd=self.cwd, stderr=subprocess.STDOUT, **kwargs)
            return output.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            fmt = "Called Processed Error:\n  cmd: %s\n  exc: %s\ncwd: %s\n  output:\n%s"
            raise Exception(fmt % (args, e, self.cwd, e.output))
        except OSError as e:
            fmt = "OS Error:\n  cmd: %s\n  exc: %s\ncwd: %s\n"
            raise Exception(fmt % (args, e, self.cwd))

    def _cmd_global(self, *args, **kwargs):
        """
        Appends the env_bin path to the executable in arg[0]
        Primarily used to run the `coverage` command
        """
        args = list(args)
        args[0] = os.path.join(self.env_bin, args[0])
        return self._cmd(*args, **kwargs)

    def _start_project(self, project_name, debug=True):
        self.project_dir = os.path.join(os.getcwd(), project_name)
        if os.path.exists(self.project_dir):
            shutil.rmtree(self.project_dir)
        output = self._cmd("django-admin.py", "startproject", project_name)
        self.assertFalse(output)
        self.settings_file = os.path.join(self.project_dir, project_name, "settings.py")
        self._add_installed_app("django_coverage_plugin")
        self._update_templates_config(debug=debug)
        # Comment this line out to view the generated project files
        self.addCleanup(shutil.rmtree, self.project_dir)
        return output

    def _add_installed_app(self, app_name):
        def _add_app(apps):
            if django.VERSION < (1, 9):
                apps = list(apps)
            apps.append(app_name)
            if django.VERSION < (1, 9):
                apps = tuple(apps)
            return apps

        with open(self.settings_file) as f:
            settings_data = f.read()
        sep = ")" if django.VERSION < (1, 9) else "]"
        settings_data = change_elem(settings_data, "INSTALLED_APPS", sep, _add_app)
        self._save_py_file(self.settings_file, settings_data)

    def _update_templates_config(self, debug=True):
        def _update_config(templates_config):
            if "APP_DIRS" in templates_config[0]:
                del templates_config[0]['APP_DIRS']
            templates_config[0]['OPTIONS']['debug'] = debug
            templates_config[0]['OPTIONS']['loaders'] = (
                'django.template.loaders.app_directories.Loader',
            )
            return templates_config

        with open(self.settings_file) as f:
            settings_data = f.read()
        settings_data = change_elem(settings_data, "TEMPLATES", "]", _update_config)
        self._save_py_file(self.settings_file, settings_data)

    def _save_py_file(self, path, data, show_data=False):
        with open(path, "w") as f:
            f.write(data)
        pyc_path = "%sc" % path
        if os.path.exists(pyc_path):
            os.remove(pyc_path)

    def _start_app(self, app_name):
        self.set_cwd(self.project_dir)
        output = self._cmd("./manage.py", "startapp", app_name)
        self.assertFalse(output)
        self._add_installed_app(app_name)

    def _run_coverage(self, *args):
        self.set_cwd(self.project_dir)
        output = self._cmd_global("coverage", "run", "--rcfile", self.config_file, *args)

        if 0:
            print("----- start output ----")
            print(output)
            print("------ end output ------")

        if "Disabling plugin" in output:
            return output, None

        env = os.environ.copy()
        env['DJANGO_SETTINGS_MODULE'] = self.settings_file
        coverage_report = self._cmd_global(
            "coverage", "report", "-m", "--rcfile", self.config_file,
            env=env
        )
        coverage_report = self.parse_coverage_report(coverage_report)
        return output, coverage_report

    def _create_django_project(self, project_name, app_name, debug):
        self.cwd = os.getcwd()
        self._start_project(project_name, debug)
        self._start_app(app_name)
        self.config_file = self._add_project_file(COVERAGE_CFG_FILE_TEXT, "coverage.cfg")
        self.template_file = self._add_project_file(
            TEMPLATE_FILE_TEXT, app_name, "templates", "target_template.html"
        )

        define_target_view = 'from app_template_render.views import target_view'
        if django.VERSION < (1, 10):
            import_reverse = "from django.core.urlresolvers import reverse"
        else:
            import_reverse = "from django.urls import reverse"

        test_views_text = TEST_VIEWS_FILE_TEXT % locals()
        self._add_project_file(test_views_text, app_name, "test_views.py")

        self.views_file = os.path.join(self.project_dir, app_name, "views.py")
        self.urls_file = os.path.join(self.project_dir, project_name, "urls.py")
        self._add_project_file("", app_name, "templatetags", "__init__.py")
        self._add_project_file(
            TEMPLATE_TAG_TEXT, app_name, "templatetags", "test_tags.py"
        )

        self._add_view_function(app_name, VIEW_FUNC_TEXT)
        self._add_url(project_name, app_name, "target_view", "target_view")

    def _add_project_file(self, file_data, *path):
        file_path = os.path.join(self.project_dir, *path)
        try:
            os.makedirs(os.path.dirname(file_path), )
        except os.error:
            pass

        with open(file_path, "w") as f:
            f.write(file_data)
        return file_path

    def _add_view_function(self, app_name, view_text):
        with open(self.views_file) as f:
            views_data = f.read()
        views_data = "%s\n%s\n" % (views_data, view_text)
        self._save_py_file(self.views_file, views_data)

    def _add_url(self, project_name, app_name, view_func, view_name):
        with open(self.urls_file) as f:
            urls_data = f.read()

        urls_data = urls_data.replace(
            "urlpatterns = [",
            "import %s.views\n\nurlpatterns = [" % app_name
        )
        if django.VERSION < (2, 0):
            url_func = "url"
        else:
            url_func = "path"

        fmt = '''    %(url_func)s(r'^%(app_name)s/', %(app_name)s.views.%(view_func)s),\n]'''
        urls_data = urls_data.replace("]", fmt % locals())

        self._save_py_file(self.urls_file, urls_data)

    def test_no_debug(self):
        self._create_django_project("integration_template_render", "app_template_render", debug=False,)
        output, coverage_report = self._run_coverage("manage.py", "test", "app_template_render")
        self.assertIn("Disabling plugin", output)
        self.assertIn("Template debugging must be enabled in settings.", output)

    def test_wrong_engine(self):
        self._create_django_project("integration_template_render", "app_template_render", debug=True)
        self._change_template_engine()
        output, coverage_report = self._run_coverage("manage.py", "test", "app_template_render")
        self.assertIn("Disabling plugin", output)
        self.assertIn("Can't use non-Django templates.", output)

    def _change_template_engine(self):
        with open(self.settings_file) as f:
            settings_data = f.read()
        settings_data = settings_data.replace(
            "django.template.backends.django.DjangoTemplates",
            "integration_template_render.settings.FakeTemplateBackend",
        )
        settings_data = settings_data.replace(
            "\nTEMPLATES = ",
            """
from django.template import TemplateDoesNotExist, TemplateSyntaxError
from django.template.backends.base import BaseEngine
from django.template.backends.utils import csrf_input_lazy, csrf_token_lazy

class Template(object):
    def __init__(self, template):
        self.template = template
    def render(self, context=None, request=None):
        return "1212 DcDc LOWER: dcdc <title>Example: 1212</title>"
class FakeTemplateBackend(BaseEngine):
    app_dirname = 'fake'

    def __init__(self, params):
        params = params.copy()
        params.pop('OPTIONS')
        super(FakeTemplateBackend, self).__init__(params)

    def from_string(self, template_code):
        return Template(template_code)

    def get_template(self, template_name):
        return Template(template_name)

TEMPLATES = """,
        )
        self._save_py_file(self.settings_file, settings_data)

    def test_template_render(self):
        self._create_django_project(
            "integration_template_render",
            "app_template_render",
            debug=True,
        )

        output, coverage_report = self._run_coverage("manage.py", "test", "app_template_render")

        self.assertNotIn("Disabling plugin", output)
        self.assertIn("\nOK\n", output)
        self.assertIn("Ran 1 test", output)
        self.assertNotIn("ERROR", output)
        self.assertNotIn("FAIL", output)

        # import pprint;pprint.pprint(coverage_report)
        self.assertIsCovered(coverage_report, "integration_template_render/settings.py")
        self.assertIsCovered(coverage_report, "integration_template_render/__init__.py")
        self.assertIsCovered(coverage_report, "integration_template_render/urls.py")

        # Different versions of Django result in different coverage for manage.py
        if django.VERSION < (1, 10):
            expect_missing, expect_pct = 0, 100
        elif django.VERSION < (2, 0):
            expect_missing, expect_pct = 6, 54
        else:
            # This includes django-tip, so it's likely to change over time.
            expect_missing, expect_pct = 2, 78
        self.assertIsCovered(coverage_report, "manage.py", expect_missing, expect_pct)

        self.assertIsCovered(coverage_report, "app_template_render/__init__.py")
        self.assertIsCovered(coverage_report, "app_template_render/views.py")
        self.assertIsCovered(coverage_report, "app_template_render/templates/target_template.html")
        self.assertIsCovered(coverage_report, "app_template_render/templatetags/test_tags.py")

    def assertIsCovered(self, cov_report, path, expect_missing=0, expect_pct=100):
        fmt = u"%s [%s] expected: %%r, got %%r"
        info = cov_report[path]
        fmt = fmt % (path, info)
        if info.num_missing != expect_missing or info.pct != expect_pct:
            missing_line_numbers = set(info.missing_line_numbers())
            full_path = os.path.join(self.project_dir, path)
            print("FILE:", full_path)
            with open(full_path) as f:
                for idx, line in enumerate(f):
                    line_no = idx + 1
                    status = "M" if line_no in missing_line_numbers else " "
                    print("%s %4s  %s" % (status, line_no, line[:-1]))

        self.assertEqual(info.num_missing, expect_missing, fmt % (expect_missing, info.num_missing))
        self.assertEqual(info.pct, expect_pct, fmt % (expect_pct, info.pct))

    def parse_coverage_report(self, report):
        class ReportInfo(object):
            def __init__(self, num_lines, num_missing, pct, missing):
                self.num_lines = num_lines
                self.num_missing = num_missing
                self.pct = int(pct[:-1])
                self.missing = missing

            def __unicode__(self):
                fmt = u"%s/%s/%s%%%%/%s"
                return fmt % (self.num_lines, self.num_missing, self.pct, self.missing)

            def __repr__(self):
                fmt = u"ReportInfo(num_lines=%r, num_missing=%r, pct=%r, missing=%r)"
                return fmt % (self.num_lines, self.num_missing, self.pct, self.missing)

            def missing_line_numbers(self):
                # generate line numbers
                for chunk in self.missing.split(","):
                    chunk = chunk.strip()
                    if not chunk:
                        continue
                    elif "-" in chunk:
                        # This is a range, so generate the lineno for each line in the range
                        start, end = chunk.split("-", 1)
                        for i in range(int(start), int(end + 1)):
                            yield i
                    else:
                        yield int(chunk)

        report_dict = {}
        for line in report.splitlines():
            if "/.tox/" in line:
                continue
            pieces = line.split(None, 4)
            if len(pieces) not in (4, 5):
                continue

            if pieces[3][-1] != '%':
                continue
            if pieces[0] in ("Name", "TOTAL"):
                continue

            if len(pieces) == 4:
                file, num_lines, num_missing, pct = pieces
                missing = ""
            elif len(pieces) == 5:
                file, num_lines, num_missing, pct, missing = pieces
            else:
                continue

            report_dict[file] = ReportInfo(int(num_lines), int(num_missing), pct, missing)
        return report_dict
