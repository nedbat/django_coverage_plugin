"""The Django coverage plugin."""

import os.path

import coverage.plugin

import django
from django.template import Lexer, Token
from django.template.base import TOKEN_MAPPING, TOKEN_BLOCK, TOKEN_VAR

from blessed import Terminal
t = Terminal()

# TODO: Add a check for TEMPLATE_DEBUG, and make noise if it is false.

class Plugin(coverage.plugin.CoveragePlugin, coverage.plugin.FileTracer):

    def __init__(self, options):
        super(Plugin, self).__init__(options)
        self.django_dir = os.path.dirname(django.__file__)
        self.django_template_dir = os.path.join(self.django_dir, "template")

        self.source_map = {}

    ## CoveragePlugin methods

    def file_tracer(self, filename):
        if filename.startswith(self.django_template_dir):
            # TODO: django/templatetags shouldn't be traced.
            return self
        return None

    def file_reporter(self, filename):
        return FileReporter(filename)

    ## FileTracer methods

    def has_dynamic_source_filename(self):
        return True

    def dynamic_source_filename(self, filename, frame):
        if frame.f_code.co_name != 'render':
            return None

        locals = frame.f_locals
        render_self = locals['self']
        if 0:
            dump_frame(frame)
        try:
            source = render_self.source
            #print t.bold_blue("source: {!r}".format(source))
            origin = source[0]
            #print t.bold_blue("origin: {!r}".format(origin.__dict__))
            filename = origin.name
            #print t.bold_red("filename: {!r}".format(filename))
            template_text = open(filename).read()
            #print "text: {!r}".format(template_text[source[1][0]:source[1][1]])
            #print
            return filename
        except (AttributeError, IndexError):
            pass
        return None

    def line_number_range(self, frame):
        assert frame.f_code.co_name == 'render'
        source = self.template_source(frame)
        line_map = self.get_line_map(source[0].name)
        start = get_line_number(line_map, source[1][0])
        end = get_line_number(line_map, source[1][1])
        if start < 0 or end < 0:
            return -1, -1
        return start, end

    ## FileTracer helpers

    def template_source(self, frame):
        render_self = frame.f_locals['self']
        return getattr(render_self, "source", None)

    def get_line_map(self, filename):
        if filename not in self.source_map:
            with open(filename) as template_file:
                template_source = template_file.read()
            line_lengths = [len(l) for l in template_source.splitlines(True)]
            self.source_map[filename] = list(running_sum(line_lengths))
        return self.source_map[filename]


class FileReporter(coverage.plugin.FileReporter):
    def __init__(self, filename):
        # TODO: do we want the .filename attribute to be part of the public API?
        self.filename = filename

    def statements(self):
        source_lines = set()

        with open(self.filename) as f:
            text = f.read()

        tokens = Lexer(text, "<string>").tokenize()

        comment = False
        for token in tokens:
            print "%10s %2d: %r" % (TOKEN_MAPPING[token.token_type], token.lineno, token.contents)
            if token.token_type == TOKEN_BLOCK:
                if token.contents == 'comment':
                    comment = True
                    continue
                elif token.contents == 'endcomment':
                    comment = False
                    continue

            if comment:
                continue

            if token.token_type == TOKEN_BLOCK or token.token_type == TOKEN_VAR:
                if token.token_type == TOKEN_BLOCK and token.contents.startswith('end'):
                    continue

                source_lines.add(token.lineno)

        return source_lines


def running_sum(seq):
    total = 0
    for num in seq:
        total += num
        yield total

def get_line_number(line_map, offset):
    for lineno, line_offset in enumerate(line_map, start=1):
        if line_offset >= offset:
            return lineno
    return -1

def dump_frame(frame):
    """Dump interesting information about this frame."""
    locals = frame.f_locals
    self = locals.get('self', None)
    if "__builtins__" in locals:
        del locals["__builtins__"]

    print "-- frame -----------------------"
    print "{}:{}:{}".format(
        os.path.basename(frame.f_code.co_filename),
        frame.f_lineno,
        type(self),
        )
    print locals
    if self:
        print "self:", self.__dict__
