# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/django_coverage_plugin/blob/master/NOTICE.txt

"""The tests for the Django Coverage Plugin."""

# Define URLs here so we can use ROOT_URLCONF="tests"

from django.conf.urls import url


def index(request):
    """A bogus view to use in the urls below."""
    pass

urlpatterns = [
    url(r'^home$', index, name='index'),
]
