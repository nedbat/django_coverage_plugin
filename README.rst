.. start-badges

|status| |kit| |license| |versions| |djversions|

.. |status| image:: https://img.shields.io/pypi/status/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Package stability
.. |kit| image:: https://badge.fury.io/py/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Latest PyPI Version
.. |license| image:: https://img.shields.io/pypi/l/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Apache 2.0 License
.. |versions| image:: https://img.shields.io/pypi/pyversions/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Supported Python Versions
.. |djversions| image:: https://img.shields.io/badge/Django-1.8%20%7C%201.11%20%7C%202.0%20%7C%202.1%20%7C%202.2%20%7C%203.0-44b78b.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Supported Django Versions

.. end-badges

==================================
Django Template Coverage.py Plugin
==================================

A `coverage.py`_ plugin to measure test coverage of Django templates.

Supported Python versions: 2.7, and 3.6 through 3.10.

Supported Django versions: 1.8, 1.11, 2.x, 3.x and 4.x.

Supported coverage.py versions: 4.x or higher.

The plugin is pip installable::

    $ pip install django_coverage_plugin

To run it, add this setting to your ``.coveragerc`` file::

    [run]
    plugins = django_coverage_plugin

Then run your tests under `coverage.py`_.

You will see your templates listed in your coverage report along with
your Python modules. Please use `coverage.py`_ v4.4 or greater to allow
the plugin to identify untested templates.

If you get a :code:`django.core.exceptions.ImproperlyConfigured` error,
you need to set the :code:`DJANGO_SETTINGS_MODULE` environment variable.

Template coverage only works if your Django templates have debugging enabled.
If you get :code:`django_coverage_plugin.plugin.DjangoTemplatePluginException:
Template debugging must be enabled in settings`, or if no templates get
measured, make sure you have :code:`TEMPLATES.OPTIONS.debug` set to True in
your settings file:

.. code-block:: python

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                'debug': True,
            },
        },
    ]


Configuration
~~~~~~~~~~~~~

The Django template plugin uses some existing settings from your
``.coveragerc`` file.  The ``source=``, ``include=``, and ``omit=`` options
control what template files are included in the report.

The plugin can find unused template and include them in your results.  By
default, it will look for files in your templates directory with an extension
of ``.html``, ``.htm``, or ``.txt``.  You can configure it to look for a different set of
extensions if you like::

    [run]
    plugins = django_coverage_plugin

    [django_coverage_plugin]
    template_extensions = html, txt, tex, email

If you use ``pyproject.toml`` for tool configuration use::

    [tool.coverage.run]
    plugins = [
        'django_coverage_plugin',
    ]

    [tool.coverage.django_coverage_plugin]
    template_extensions = 'html, txt, tex, email'

Caveats
~~~~~~~

Coverage.py can't tell whether a ``{% blocktrans %}`` tag used the
singular or plural text, so both are marked as used if the tag is used.


What the? How?
~~~~~~~~~~~~~~

The technique used to measure the coverage is the same that Dmitry
Trofimov used in `dtcov`_, but integrated into coverage.py as a plugin,
and made more performant. I'd love to see how well it works in a real
production project. If you want to help me with it, feel free to drop me
an email.

The coverage.py plugin mechanism is designed to be generally useful for
hooking into the collection and reporting phases of coverage.py,
specifically to support non-Python files.  If you have non-Python files
you'd like to support in coverage.py, let's talk.


Tests
~~~~~

To run the tests::

    $ pip install -r requirements.txt
    $ tox


History
~~~~~~~

Unreleased
----------

Add support for Django 4.0

v2.0.2 — 2021-11-11
-------------------

If a non-UTF8 file was found when looking for templates, it would fail when
reading during the reporting phase, ending execution.  This failure is now
raised in a way that can be ignored with a .coveragerc setting of ``[report]
ignore_errors=True`` (`issue 78`_).

When using ``source=.``, an existing coverage HTML report directory would be
found and believed to be unmeasured HTML template files.  This is now fixed.

.. _issue 78: https://github.com/nedbat/django_coverage_plugin/issues/78


v2.0.1 — 2021-10-06
-------------------

Test and claim our support on Python 3.10.

v2.0.0 — 2021-06-08
-------------------

Drop support for Python 3.4 and 3.5.

A setting is available: ``template_extensions`` lets you set the file
extensions that will be considered when looking for unused templates
(requested in `issue 60`_).

Fix an issue on Windows where file names were being compared
case-sensitively, causing templates to be missed (`issue 46`_).

Fix an issue (`issue 63`_) where tag libraries can't be found if imported
during test collection. Thanks to Daniel Izquierdo for the fix.

.. _issue 46: https://github.com/nedbat/django_coverage_plugin/issues/46
.. _issue 60: https://github.com/nedbat/django_coverage_plugin/issues/60
.. _issue 63: https://github.com/nedbat/django_coverage_plugin/issues/63

v1.8.0 — 2020-01-23
-------------------

Add support for:

- Coverage 5

v1.7.0 — 2020-01-16
-------------------

Add support for:

- Python 3.7 & 3.8
- Django 2.2 & 3.0

v1.6.0 — 2018-09-04
-------------------

Add support for Django 2.1.


v1.5.2 — 2017-10-18
-------------------

Validates support for Django version 2.0b1. Improves discovery of
template files.


v1.5.1a — 2017-04-05
--------------------

Validates support for Django version 1.11. Testing for new package
maintainer Pamela McA'Nulty


v1.5.0 — 2017-02-23
-------------------

Removes support for Django versions below 1.8.  Validates support for
Django version 1.11b1


v1.4.2 — 2017-02-06
-------------------

Fixes another instance of `issue 32`_, which was the result of an
initialization order problem.



v1.4.1 — 2017-01-25
-------------------

Fixes `issue 32`_, which was the result of an initialization order
problem.

.. _issue 32: https://github.com/nedbat/django_coverage_plugin/issues/32



v1.4 — 2017-01-16
-----------------

Django 1.10.5 is now supported.

Checking settings configuration is deferred so that settings.py is
included in coverage reporting.  Fixes `issue 28`_.

Only the ``django.template.backends.django.DjangoTemplates`` template
engine is supported, and it must be configured with
``['OPTIONS']['debug'] = True``. Fixes `issue 27`_.

.. _issue 28: https://github.com/nedbat/django_coverage_plugin/issues/28
.. _issue 27: https://github.com/nedbat/django_coverage_plugin/issues/27



v1.3.1 — 2016-06-02
-------------------

Settings are read slightly differently, so as to not interfere with
programs that don't need settings.  Fixes `issue 18`_.

.. _issue 18: https://github.com/nedbat/django_coverage_plugin/issues/18



v1.3 — 2016-04-03
-----------------

Multiple template engines are allowed.  Thanks, Simon Charette.



v1.2.2 — 2016-02-01
-------------------

No change in code, but Django 1.9.2 is now supported.



v1.2.1 — 2016-01-28
-------------------

The template debug settings are checked properly for people still using
``TEMPLATE_DEBUG`` in newer versions of Django.



v1.2 — 2016-01-16
-----------------

Check if template debugging is enabled in the settings, and raise a
visible warning if not.  This prevents mysterious failures of the
plugin, and fixes `issue 17`_.

Potential Django 1.9 support is included, but the patch to Django hasn't
been applied yet.

.. _issue 17: https://github.com/nedbat/django_coverage_plugin/issues/17



v1.1 — 2015-11-12
-----------------

Explicitly configure settings if need be to get things to work.



v1.0 — 2015-09-20
-----------------

First version :)

.. _coverage.py: http://nedbatchelder.com/code/coverage
.. _dtcov: https://github.com/traff/dtcov
