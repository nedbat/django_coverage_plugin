Django Template Coverage Plugin
===============================

A `coverage.py`_ plugin to measure the coverage of Django templates.

Supported Python versions are 2.7 and 3.4.  Supported Django versions are 1.4
through 1.8.

The plugin itself is pip installable::

    $ pip install django_coverage_plugin

To run it, add this setting to your .coveragerc::

    [run]
    plugins =
        django_coverage_plugin

Then run your tests under coverage.py. It requires the latest coverage.py, so
it may not work with other coverage-related tools such as test-runner coverage
plugins, or coveralls.io.

You will see your templates listed in your coverage report alongside your
Python modules.

If you get a django.core.exceptions.ImproperlyConfigured error, you need to set
the DJANGO_SETTINGS_MODULE environment variable.


Configuration
-------------

The Django template plugin uses some existing settings from your .coveragerc
file.  The ``source=``, ``include=``, and ``omit=`` options control what
template files are included in the report.


Caveats
-------

Files included by the `{% ssi %}` tag are not included in the coverage
measurements.

Coverage can't tell whether a `{% blocktrans %}` tag used the singular or
plural text, so both are marked as used if the tag is used.


What the? How?
--------------

The technique used to measure the coverage is the same that Dmitry Trofimov
used in `dtcov`_, but integrated into coverage.py as a plugin, and made more
performant. I'd love to see how well it works in a real production project. If
you want to help me with it, feel free to drop me an email.

The coverage.py plugin mechanism is designed to be generally useful for hooking
into the collection and reporting phases of coverage.py, specifically to
support non-Python files.  If you have non-Python files you'd like to support
in coverage.py, let's talk.


Tests
-----

To run the tests::

    $ pip install -r requirements.txt
    $ tox


.. _coverage.py: http://nedbatchelder.com/code/coverage
.. _dtcov: https://github.com/traff/dtcov
