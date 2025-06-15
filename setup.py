#!/usr/bin/env python
"""Setup for Django Coverage Plugin

Licensed under the Apache 2.0 License
- http://www.apache.org/licenses/LICENSE-2.0
- https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""

import re
from os.path import dirname, join

from setuptools import setup


def read(*names, **kwargs):
    """Read and return contents of file

    Parameter: encoding kwarg may be set
    """
    with open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as f:
        return f.read()


classifiers = """\
Environment :: Console
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: 3.11
Programming Language :: Python :: 3.12
Programming Language :: Python :: 3.13
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
Development Status :: 5 - Production/Stable
Framework :: Django
Framework :: Django :: 2.2
Framework :: Django :: 3.2
Framework :: Django :: 4.2
Framework :: Django :: 5.2
"""

setup(
    name='django_coverage_plugin',
    version='3.1.0',
    description='Django template coverage.py plugin',
    long_description=(
        re.sub(
            '(?ms)^.. start-badges.*^.. end-badges',
            '',
            read('README.rst'),
        )
    ),
    long_description_content_type='text/x-rst',
    author='Ned Batchelder',
    author_email='ned@nedbatchelder.com',
    url='https://github.com/nedbat/django_coverage_plugin',
    packages=['django_coverage_plugin'],
    install_requires=[
        'coverage',
    ],
    license='Apache-2.0',
    classifiers=classifiers.splitlines(),
)
