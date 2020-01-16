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

Supported Python versions: 2.7, 3.4, 3.5, 3.6, 3.7 and 3.8.

Supported Django versions: 1.8, 1.11, 2.0, 2.1, 2.2 and 3.0.

Supported coverage.py version 4.x . Support for version 5 is on the way!

The plugin is pip installable::

    $ pip install django_coverage_plugin

To run it, add this setting to your ``.coveragerc`` file::

    [run]
    plugins =
        django_coverage_plugin

Then run your tests under `coverage.py`_.

You will see your templates listed in your coverage report along with
your Python modules. Please use `coverage.py`_ v4.4 or greater to allow
the plugin to identify untested templates.

If you get a :code:`django.core.exceptions.ImproperlyConfigured` error,
you need to set the :code:`DJANGO_SETTINGS_MODULE` environment variable.


Configuration
~~~~~~~~~~~~~

The Django template plugin uses some existing settings from your
.coveragerc file.  The ``source=``, ``include=``, and ``omit=`` options
control what template files are included in the report.


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

.. _coverage.py: http://nedbatchelder.com/code/coverage
.. _dtcov: https://github.com/traff/dtcov
