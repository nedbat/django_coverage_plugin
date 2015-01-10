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
