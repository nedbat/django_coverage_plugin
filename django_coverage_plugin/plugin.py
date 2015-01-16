"""The Django coverage plugin."""

from __future__ import print_function, unicode_literals

import os.path
from six.moves import range

import coverage.plugin

import django
from django.template import Lexer, TextNode
from django.template.base import TOKEN_MAPPING
from django.template import TOKEN_BLOCK, TOKEN_TEXT, TOKEN_VAR


SHOW_PARSING = False
SHOW_TRACING = False

if 0:
    from blessed import Terminal
    t = Terminal()

# TODO: Add a check for TEMPLATE_DEBUG, and make noise if it is false.


class Plugin(coverage.plugin.CoveragePlugin, coverage.plugin.FileTracer):

    def __init__(self, options):
        super(Plugin, self).__init__(options)
        self.django_dir = os.path.dirname(django.__file__)
        self.django_template_dir = os.path.join(self.django_dir, "template")

        self.source_map = {}

    # --- CoveragePlugin methods

    def file_tracer(self, filename):
        if filename.startswith(self.django_template_dir):
            if "templatetags" not in filename:
                return self
        return None

    def file_reporter(self, filename):
        return FileReporter(filename)

    # --- FileTracer methods

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
            origin = source[0]
            filename = origin.name
            return filename
        except (AttributeError, IndexError):
            pass
        return None

    def line_number_range(self, frame):
        assert frame.f_code.co_name == 'render'
        render_self = frame.f_locals['self']
        source = render_self.source
        if SHOW_TRACING:
            print("{!r}: {}".format(render_self, source))
        s_start, s_end = source[1]
        if isinstance(render_self, TextNode):
            text = render_self.s
            first_line = text.splitlines(True)[0]
            if first_line.isspace():
                s_start += len(first_line)
        line_map = self.get_line_map(source[0].name)
        start = get_line_number(line_map, s_start)
        end = get_line_number(line_map, s_end-1)
        if start < 0 or end < 0:
            return -1, -1
        return start, end

    # --- FileTracer helpers

    def get_line_map(self, filename):
        """The line map for `filename`.

        A line map is a list of character offsets, indicating where each line
        in the text begins.  For example, a line map like this::

            [13, 19, 30]

        means that line 2 starts at character 13, line 3 starts at 19, etc.
        Line 1 always starts at character 0.

        """
        if filename not in self.source_map:
            with open(filename) as template_file:
                template_source = template_file.read()
                if 0:   # change to see the template text
                    for i in range(0, len(template_source), 10):
                        print("%3d: %r" % (i, template_source[i:i+10]))
            self.source_map[filename] = make_line_map(template_source)
        return self.source_map[filename]


class FileReporter(coverage.plugin.FileReporter):
    def __init__(self, filename):
        # TODO: do we want the .filename attribute to be part of the public
        # API of the coverage plugin?
        self.filename = filename
        # TODO: is self.name required? Can the base class provide it somehow?
        self.name = os.path.basename(filename)
        # TODO: html filenames are absolute.

    def statements(self):
        source_lines = set()

        if SHOW_PARSING:
            print("-------------- {}".format(self.filename))

        with open(self.filename) as f:
            text = f.read()

        tokens = Lexer(text, self.filename).tokenize()

        # Are we inside a comment?
        comment = False
        # Is this a template that extends another template?
        extends = False
        # Are we inside a block?
        inblock = False

        for token in tokens:
            if SHOW_PARSING:
                print(
                    "%10s %2d: %r" % (
                        TOKEN_MAPPING[token.token_type],
                        token.lineno,
                        token.contents,
                    )
                )
            if token.token_type == TOKEN_BLOCK:
                if token.contents == 'endcomment':
                    comment = False
                    continue

            if comment:
                continue

            if token.token_type == TOKEN_BLOCK:
                if token.contents.startswith("endblock"):
                    inblock = False
                elif token.contents.startswith("block"):
                    inblock = True
                    if extends:
                        continue

                if token.contents == 'comment':
                    comment = True
                if token.contents.startswith("end"):
                    continue
                elif token.contents in ("else", "empty"):
                    continue
                elif token.contents.startswith("elif"):
                    # NOTE: I don't like this, I want to be able to trace elif
                    # nodes, but the Django template engine doesn't track them
                    # in a way that we can get useful information from them.
                    continue
                elif token.contents.startswith("extends"):
                    extends = True

                source_lines.add(token.lineno)

            elif token.token_type == TOKEN_VAR:
                source_lines.add(token.lineno)

            elif token.token_type == TOKEN_TEXT:
                if extends and not inblock:
                    continue
                # Text nodes often start with newlines, but we don't want to
                # consider that first line to be part of the text.
                lineno = token.lineno
                lines = token.contents.splitlines(True)
                num_lines = len(lines)
                if lines[0].isspace():
                    lineno += 1
                    num_lines -= 1
                source_lines.update(range(lineno, lineno+num_lines))

            if SHOW_PARSING:
                print("\t\t\tNow source_lines is: {!r}".format(source_lines))

        return source_lines


def running_sum(seq):
    total = 0
    for num in seq:
        total += num
        yield total


def make_line_map(text):
    line_lengths = [len(l) for l in text.splitlines(True)]
    line_map = list(running_sum(line_lengths))
    return line_map


def get_line_number(line_map, offset):
    """Find a line number, given a line map and a character offset."""
    for lineno, line_offset in enumerate(line_map, start=1):
        if line_offset > offset:
            return lineno
    return -1


def dump_frame(frame):
    """Dump interesting information about this frame."""
    locals = frame.f_locals
    self = locals.get('self', None)
    if "__builtins__" in locals:
        del locals["__builtins__"]

    print("-- frame -----------------------")
    print("{}:{}:{}".format(
        os.path.basename(frame.f_code.co_filename),
        frame.f_lineno,
        type(self),
        ))
    print(locals)
    if self:
        print("self:", self.__dict__)
