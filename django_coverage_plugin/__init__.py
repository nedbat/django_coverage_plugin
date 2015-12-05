"""Django Template Coverage Plugin"""

from .plugin import DjangoTemplatePlugin
from .plugin import DjangoTemplatePluginException       # noqa


def coverage_init(reg, options):
    reg.add_file_tracer(DjangoTemplatePlugin())
