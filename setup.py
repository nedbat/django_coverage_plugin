#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Setup for Django Coverage Plugin

Licensed under the Apache 2.0 License
- http://www.apache.org/licenses/LICENSE-2.0
- https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""
from __future__ import absolute_import, print_function

import io
import re
from os.path import dirname, join

from setuptools import setup


def read(*names, **kwargs):
    """Read and return contents of file

    Parameter: encoding kwarg may be set
    """
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


classifiers = """\
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
Development Status :: 5 - Production/Stable
Framework :: Django
Framework :: Django :: 1.8
Framework :: Django :: 1.11
Framework :: Django :: 2.0
Framework :: Django :: 2.1
Framework :: Django :: 2.2
Framework :: Django :: 3.0
"""

setup(
    name='django_coverage_plugin',
    version='1.8.0',
    description='Django template coverage.py plugin',
    long_description=(
        re.compile(
            '^.. start-badges.*^.. end-badges',
            re.M | re.S,
        ).sub('', read('README.rst'))
    ),
    author='Ned Batchelder',
    author_email='ned@nedbatchelder.com',
    url='https://github.com/nedbat/django_coverage_plugin',
    packages=['django_coverage_plugin'],
    install_requires=[
        'coverage',
        'six >= 1.4.0',
    ],
    license='Apache 2.0',
    classifiers=classifiers.splitlines(),
)
