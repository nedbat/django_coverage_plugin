.. Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
.. For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

==================================
Django Template Coverage.py Plugin
==================================

A `coverage.py`_ plugin to measure the coverage of Django templates.

| |license| |versions| |djversions| |status|
| |kit| |downloads|

Supported Python versions are 2.7, 3.4, and 3.5.  Supported Django versions are
1.4 through 1.9.

The plugin is pip installable::

    $ pip install django_coverage_plugin

To run it, add this setting to your .coveragerc file::

    [run]
    plugins =
        django_coverage_plugin

Then run your tests under coverage.py. It requires coverage.py 4.0 or later.

You will see your templates listed in your coverage report along with your
Python modules.

If you get a django.core.exceptions.ImproperlyConfigured error, you need to set
the DJANGO_SETTINGS_MODULE environment variable.


Configuration
~~~~~~~~~~~~~

The Django template plugin uses some existing settings from your .coveragerc
file.  The ``source=``, ``include=``, and ``omit=`` options control what
template files are included in the report.


Caveats
~~~~~~~

Files included by the ``{% ssi %}`` tag are not included in the coverage
measurements.

Coverage.py can't tell whether a ``{% blocktrans %}`` tag used the singular or
plural text, so both are marked as used if the tag is used.


Changes
~~~~~~~


v1.3.1 --- 2016-06-02
---------------------

Settings are read slightly differently, so as to not interfere with programs
that don't need settings.  Fixes `issue 18`_.

.. _issue 18: https://github.com/nedbat/django_coverage_plugin/issues/18


v1.3 --- 2016-04-03
-------------------

Multiple template engines are allowed.  Thanks, Simon Charette.


v1.2.2 --- 2016-02-01
---------------------

No change in code, but Django 1.9.2 is now supported.


v1.2.1 --- 2016-01-28
---------------------

The template debug settings are checked properly for people still using
``TEMPLATE_DEBUG`` in newer versions of Django.


v1.2 --- 2016-01-16
-------------------

Check if template debugging is enabled in the settings, and raise a visible
warning if not.  This prevents mysterious failures of the plugin, and fixes
`issue 17`_.

Potential Django 1.9 support is included, but the patch to Django hasn't been
applied yet.

.. _issue 17: https://github.com/nedbat/django_coverage_plugin/issues/17


v1.1 --- 2015-11-12
-------------------

Explicitly configure settings if need be to get things to work.


v1.0 --- 2015-09-20
-------------------

First version :)


What the? How?
~~~~~~~~~~~~~~

The technique used to measure the coverage is the same that Dmitry Trofimov
used in `dtcov`_, but integrated into coverage.py as a plugin, and made more
performant. I'd love to see how well it works in a real production project. If
you want to help me with it, feel free to drop me an email.

The coverage.py plugin mechanism is designed to be generally useful for hooking
into the collection and reporting phases of coverage.py, specifically to
support non-Python files.  If you have non-Python files you'd like to support
in coverage.py, let's talk.


Tests
~~~~~

To run the tests::

    $ pip install -r requirements.txt
    $ tox


.. _coverage.py: http://nedbatchelder.com/code/coverage
.. _dtcov: https://github.com/traff/dtcov


.. |license| image:: https://img.shields.io/pypi/l/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: License
.. |versions| image:: https://img.shields.io/pypi/pyversions/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Python versions supported
.. |djversions| image:: https://img.shields.io/badge/Django-1.4, 1.5, 1.6, 1.7, 1.8, 1.9-44b78b.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Django versions supported
.. |status| image:: https://img.shields.io/pypi/status/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Package stability
.. |kit| image:: https://badge.fury.io/py/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: PyPI status
.. |downloads| image:: https://img.shields.io/pypi/dm/django_coverage_plugin.svg
    :target: https://pypi.python.org/pypi/django_coverage_plugin
    :alt: Monthly PyPI downloads
