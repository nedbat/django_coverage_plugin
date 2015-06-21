"""The Django coverage plugin."""

from __future__ import print_function

import os.path

from six.moves import range

import coverage.plugin

import django.template
from django.template.base import (
    Lexer, TextNode,
    TOKEN_BLOCK, TOKEN_MAPPING, TOKEN_TEXT, TOKEN_VAR,
    )
from django.templatetags.i18n import BlockTranslateNode
try:
    from django.template.defaulttags import VerbatimNode
except ImportError:
    # Django 1.4 didn't have VerbatimNode
    VerbatimNode = None


SHOW_PARSING = False
SHOW_TRACING = False

# TODO: Add a check for TEMPLATE_DEBUG, and make noise if it is false.


def read_template_source(filename):
    """Read the source of a Django template, returning the Unicode text."""
    # Import this late to be sure we don't trigger settings machinery too
    # early.
    from django.conf import settings

    with open(filename, "rb") as f:
        text = f.read().decode(settings.FILE_CHARSET)

    return text


class Plugin(coverage.plugin.CoveragePlugin, coverage.plugin.FileTracer):

    def __init__(self, options):
        super(Plugin, self).__init__(options)
        self.django_template_dir = os.path.realpath(
            os.path.dirname(django.template.__file__)
        )

        self.source_map = {}

    # --- CoveragePlugin methods

    def sys_info(self):
        return [
            ("django_template_dir", self.django_template_dir),
            ("environment", sorted(
                ("%s = %s" % (k, v))
                for k, v in os.environ.items()
                if "DJANGO" in k
            )),
        ]

    def file_tracer(self, filename):
        if filename.startswith(self.django_template_dir):
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
            filename = render_self.source[0].name
            if filename.startswith("<"):
                # String templates have a filename of "<unknown source>", and
                # can't be reported on later, so ignore them.
                return None
            return filename
        except (AttributeError, IndexError):
            pass
        return None

    def line_number_range(self, frame):
        assert frame.f_code.co_name == 'render'
        if 0:
            dump_frame(frame, label="line_number_range")
        render_self = frame.f_locals['self']
        source = render_self.source
        if SHOW_TRACING:
            print("{!r}: {}".format(render_self, source))
        s_start, s_end = source[1]
        if isinstance(render_self, TextNode):
            first_line = render_self.s.splitlines(True)[0]
            if first_line.isspace():
                s_start += len(first_line)
        elif VerbatimNode and isinstance(render_self, VerbatimNode):
            # VerbatimNode doesn't track source the same way. s_end only points
            # to the end of the {% verbatim %} opening tag, not the entire
            # content. Adjust it to cover all of it.
            s_end += len(render_self.content)
        elif isinstance(render_self, BlockTranslateNode):
            # BlockTranslateNode has a list of text and variable tokens.
            # Get the end of the contents by looking at the last token,
            # and use its endpoint.
            last_tokens = render_self.plural or render_self.singular
            s_end = last_tokens[-1].source[1][1]
        line_map = self.get_line_map(source[0].name)
        start = get_line_number(line_map, s_start)
        end = get_line_number(line_map, s_end-1)
        if start < 0 or end < 0:
            start, end = -1, -1
        if SHOW_TRACING:
            print("line_number_range({}) -> {}".format(
                source[0].name, (start, end)
            ))
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
            template_source = read_template_source(filename)
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
        # TODO: html filenames are absolute.

        self._source = None

    def source(self):
        if self._source is None:
            self._source = read_template_source(self.filename)
        return self._source

    def statements(self):
        source_lines = set()

        if SHOW_PARSING:
            print("-------------- {}".format(self.filename))

        tokens = Lexer(self.source(), self.filename).tokenize()

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
                if token.contents == "endcomment":
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

                if extends and not inblock:
                    # In an inheriting tempalte, ignore all tags outside of
                    # blocks.
                    continue

                if token.contents == "comment":
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


def dump_frame(frame, label=""):
    """Dump interesting information about this frame."""
    locals = dict(frame.f_locals)
    self = locals.get('self', None)
    if "__builtins__" in locals:
        del locals["__builtins__"]

    if label:
        label = " ( %s ) " % label
    print("-- frame --%s---------------------" % label)
    print("{}:{}:{}".format(
        os.path.basename(frame.f_code.co_filename),
        frame.f_lineno,
        type(self),
        ))
    print(locals)
    if self:
        print("self:", self.__dict__)
    print("\\--")
