Django Template Coverage Plugin
===============================

A coverage.py plugin to measure the coverage of Django templates.

Details of how to use it are in this `blog post`_.  Real docs are TBD.

.. _blog post: http://nedbatchelder.com/blog/201501/coveragepy_for_django_templates.html


To run the tests on Python 2.7::

    $ pip install -r requirements.txt
    $ tox


Yet to be done
--------------

- Plugins can provide data to "debug sys".

- Specialize debug tracing?

- Figure out the path to the template so they aren't just simple file names
  in the reports.

- How to find unexecuted templates?

- Docs
