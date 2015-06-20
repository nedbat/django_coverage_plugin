"""The tests for the Django Coverage Plugin."""

# Define URLs here so we can use ROOT_URLCONF="tests"

from django.conf.urls import url


def index(request):
    """A bogus view to use in the urls below."""
    pass

urlpatterns = [
    url(r'^home$', index, name='index'),
]
