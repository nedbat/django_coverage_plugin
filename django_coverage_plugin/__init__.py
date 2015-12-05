"""Django Template Coverage Plugin"""

from .plugin import DjangoTemplatePlugin, DjangoTemplatePluginException


def coverage_init(reg, options):
    reg.add_file_tracer(DjangoTemplatePlugin())
