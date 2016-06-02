#!/usr/bin/env python
# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

from setuptools import setup

classifiers = """\
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Quality Assurance
Topic :: Software Development :: Testing
Development Status :: 5 - Production/Stable
"""

setup(
    name='django_coverage_plugin',
    version='1.3.1',
    description='Django template coverage.py plugin',
    author='Ned Batchelder',
    author_email='ned@nedbatchelder.com',
    url='https://github.com/nedbat/django_coverage_plugin',
    packages=['django_coverage_plugin'],
    install_requires=[
        'Django >= 1.4',
        'coverage >= 4.0',
        'six >= 1.4.0',
    ],
    license='Apache 2.0',
    classifiers=classifiers.splitlines(),
)
