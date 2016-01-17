# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""For printing the versions from tox.ini."""

from __future__ import print_function

import platform
import django

print(
    "{} {}; Django {}".format(
        platform.python_implementation(),
        platform.python_version(),
        django.get_version()
    )
)
