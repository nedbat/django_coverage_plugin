=======
History
=======

v1.7.0 --- 2020-01-16
---------------------

Add support for:

- Python 3.7 & 3.8
- Django 2.2 & 3.0

v1.6.0 --- 2018-09-04
---------------------

Add support for Django 2.1.


v1.5.2 --- 2017-10-18
---------------------

Validates support for Django version 2.0b1. Improves discovery of
template files.


v1.5.1a --- 2017-04-05
----------------------

Validates support for Django version 1.11. Testing for new package
maintainer Pamela McA'Nulty


v1.5.0 --- 2017-02-23
---------------------

Removes support for Django versions below 1.8.  Validates support for
Django version 1.11b1


v1.4.2 --- 2017-02-06
---------------------

Fixes another instance of `issue 32`_, which was the result of an
initialization order problem.



v1.4.1 --- 2017-01-25
---------------------

Fixes `issue 32`_, which was the result of an initialization order
problem.

.. _issue 32: https://github.com/nedbat/django_coverage_plugin/issues/32



v1.4 --- 2017-01-16
-------------------

Django 1.10.5 is now supported.

Checking settings configuration is deferred so that settings.py is
included in coverage reporting.  Fixes `issue 28`_.

Only the ``django.template.backends.django.DjangoTemplates`` template
engine is supported, and it must be configured with
``['OPTIONS']['debug'] = True``. Fixes `issue 27`_.

.. _issue 28: https://github.com/nedbat/django_coverage_plugin/issues/28
.. _issue 27: https://github.com/nedbat/django_coverage_plugin/issues/27



v1.3.1 --- 2016-06-02
---------------------

Settings are read slightly differently, so as to not interfere with
programs that don't need settings.  Fixes `issue 18`_.

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

Check if template debugging is enabled in the settings, and raise a
visible warning if not.  This prevents mysterious failures of the
plugin, and fixes `issue 17`_.

Potential Django 1.9 support is included, but the patch to Django hasn't
been applied yet.

.. _issue 17: https://github.com/nedbat/django_coverage_plugin/issues/17



v1.1 --- 2015-11-12
-------------------

Explicitly configure settings if need be to get things to work.



v1.0 --- 2015-09-20
-------------------

First version :)
