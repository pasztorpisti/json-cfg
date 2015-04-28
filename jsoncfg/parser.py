from .compatibility import xrange, unichr, utf8chr, is_unicode
from .exceptions import JSONConfigException


class ParserException(JSONConfigException):
    def __init__(self, parser, error_message):
        self.error_message = error_message
        self.line = parser.line + 1
        self.column = parser.column + 1
        message = '%s [line=%s;col=%s]' % (error_message, self.line, self.column)
        super(ParserException, self).__init__(message)


class TextParser(object):
    def __init__(self):
        super(TextParser, self).__init__()
        self.text = None
        self.pos = 0
        self.end = 0
        self.line = 0
        self.line_pos = 0
        self.prev_newline_char = None

    @property
    def column(self):
        # FIXME: Should we handle tab sizes? What tabsize to use?
        return self.pos - self.line_pos

    def init_text_parser(self, text):
        assert self.text is None
        self.text = text
        self.end = len(text)

    def error(self, message):
        raise ParserException(self, message)

    def skip_chars(self, target_pos, is_char_skippable_func):
        assert self.pos <= target_pos <= self.end
        target_pos = min(target_pos, self.end)
        for self.pos in xrange(self.pos, target_pos):
            c = self.text[self.pos]
            if not is_char_skippable_func(c):
                break
            if c in '\r\n':
                if self.prev_newline_char is not None and self.prev_newline_char != c:
                    # this is the second char of a CRLF or LFCR
                    self.prev_newline_char = None
                    self.line_pos += 1
                else:
                    self.prev_newline_char = c
                    self.line += 1
                    self.line_pos = self.pos + 1
            else:
                self.prev_newline_char = None
        else:
            self.pos = target_pos

    def skip_to(self, target_pos):
        self.skip_chars(target_pos, lambda c: True)

    def skip_char(self):
        self.skip_to(self.pos + 1)

    def peek(self, offset=0):
        pos = self.pos + offset
        if pos >= self.end:
            return None
        return self.text[pos]

    def expect(self, c):
        if self.peek() != c:
            self.error('Expected "%c"' % (c,))
        self.skip_char()


class JSONParser(TextParser):
    spaces = set(' \t\r\n')
    special_chars = set('{}[]",:/*')
    spaces_and_special_chars = spaces | special_chars

    def __init__(self, allow_comments=True, allow_unquoted_keys=True, allow_trailing_commas=True):
        super(JSONParser, self).__init__()
        self.allow_comments = allow_comments
        self.allow_unquoted_keys = allow_unquoted_keys
        self.allow_trailing_commas = allow_trailing_commas
        self.listener = None

    def parse(self, json_text, listener, root_is_array=False):
        listener.begin_parsing(self)
        try:
            self.init_text_parser(json_text)
            self.listener = listener

            c = self._skip_spaces_and_peek()
            if c == '{':
                if root_is_array:
                    self.error('The root of the json is expected to be an array!')
                self._parse_object()
            elif c == '[':
                if not root_is_array:
                    self.error('The root of the json is expected to be an object!')
                self._parse_array()
            else:
                self.error('The json string should start with "%s"' % ('[' if root_is_array else '{'))

            if self._skip_spaces_and_peek() is not None:
                self.error('Garbage detected after the parsed json!')
        finally:
            listener.end_parsing()

    def _skip_spaces_and_peek(self):
        """ Skips all spaces and comments.
        :return: The first character that follows the skipped spaces and comments or
                None if the end of the json string has been reached.
        """
        while 1:
            # skipping spaces
            self.skip_chars(self.end, lambda c: c in self.spaces)
            c = self.peek()
            if not self.allow_comments:
                return c
            if c != '/':
                return c
            d = self.peek(1)
            if d == '/':
                self.skip_to(self.pos + 2)
                self._skip_singleline_comment()
            elif d == '*':
                self.skip_to(self.pos + 2)
                self._skip_multiline_comment()
            else:
                return c

    def _skip_singleline_comment(self):
        for pos in xrange(self.pos, self.end):
            if self.text[pos] in '\r\n':
                self.skip_to(pos + 1)
                break
        else:
            self.skip_to(self.end)

    def _skip_multiline_comment(self):
        for pos in xrange(self.pos, self.end-1):
            if self.text[pos] == '*' and self.text[pos+1] == '/':
                self.skip_to(pos + 2)
                return
        self.error('Multiline comment isn\'t closed.')

    def _parse_object(self):
        assert self.peek() == '{'
        self.listener.begin_object()
        self.skip_char()
        first_item = True
        while 1:
            c = self._skip_spaces_and_peek()
            if c == '}':
                self.skip_char()
                self.listener.end_object()
                break

            if not first_item:
                self.expect(',')

                c = self._skip_spaces_and_peek()
                if c == '}':
                    if not self.allow_trailing_commas:
                        self.error('Trailing commas aren\'t enabled for this parser.')
                    self.skip_char()
                    self.listener.end_object()
                    break

            key, key_quoted, pos_after_literal = self._parse_and_return_literal(self.allow_unquoted_keys)
            self.listener.begin_object_item(key, key_quoted)
            # We step self.pos and self.line only after a successful call to the listener
            # because in case of an exception that is raised from the listener we want the
            # line/column number to point to the beginning of the parsed literal.
            self.skip_to(pos_after_literal)

            c = self._skip_spaces_and_peek()
            if c != ':':
                self.error('Expected ":"')
            self.skip_char()

            self._parse_value()

            first_item = False

    def _parse_array(self):
        assert self.peek() == '['
        self.listener.begin_array()
        self.skip_char()
        first_item = True
        while 1:
            c = self._skip_spaces_and_peek()
            if c == ']':
                self.skip_char()
                self.listener.end_array()
                break

            if not first_item:
                self.expect(',')

                c = self._skip_spaces_and_peek()
                if c == ']':
                    if not self.allow_trailing_commas:
                        self.error('Trailing commas aren\'t enabled for this parser.')
                    self.skip_char()
                    self.listener.end_array()
                    break

            self._parse_value()
            first_item = False

    def _parse_and_return_literal(self, allow_unquoted):
        c = self._skip_spaces_and_peek()
        quoted = c == '"'
        if not quoted and not allow_unquoted:
            self.error('Unquoted keys arn\'t allowed.')

        if not quoted:
            begin = self.pos
            for end in xrange(self.pos, self.end):
                if self.text[end] in self.spaces_and_special_chars:
                    break
            else:
                end = self.end
            if begin == end:
                self.error('Expected a literal here.')
            return self.text[begin:end], quoted, end

        result = []
        pos = self.pos + 1
        segment_begin = pos
        my_chr = unichr if is_unicode(self.text) else utf8chr
        while pos < self.end:
            c = self.text[pos]
            if c < ' ' and c != '\t':
                self.skip_to(pos)
                self.error('Encountered a control character that isn\'t allowed in quoted strings.')
            elif c == '"':
                if segment_begin < pos:
                    result.append(self.text[segment_begin:pos])
                pos += 1
                break
            elif c == '\\':
                if segment_begin < pos:
                    result.append(self.text[segment_begin:pos])
                pos += 1
                if pos >= self.end:
                    self.error('Reached the end of stream while parsing quoted string.')
                c = self.text[pos]
                if c == 'u':
                    if self.end - pos < 5:
                        self.error('Reached the end of stream while parsing quoted string.')
                    pos += 1
                    try:
                        codepoint = int(self.text[pos:pos+4], 16)
                    except ValueError:
                        self.skip_to(pos - 2)
                        self.error('Error decoding unicode escape sequence.')
                    else:
                        result.append(my_chr(codepoint))
                        pos += 4
                else:
                    d = {
                        '\\': '\\',
                        '/': '/',
                        '"': '"',
                        'b': '\b',
                        'f': '\f',
                        't': '\t',
                        'r': '\r',
                        'n': '\n',
                    }.get(c)
                    if d is None:
                        self.skip_to(pos - 1)
                        self.error('Quoted string contains an invalid escape sequence.')
                    result.append(d)
                    pos += 1
                segment_begin = pos
            else:
                pos += 1
        return ''.join(result), quoted, pos

    def _parse_literal(self):
        literal, quoted, pos_after_literal = self._parse_and_return_literal(True)
        self.listener.literal(literal, quoted)
        self.skip_to(pos_after_literal)

    def _parse_value(self):
        c = self._skip_spaces_and_peek()
        if c == '{':
            self._parse_object()
        elif c == '[':
            self._parse_array()
        else:
            self._parse_literal()


class ParserListener(object):
    def __init__(self):
        super(ParserListener, self).__init__()
        self.parser = None

    def error(self, message):
        raise ParserException(self.parser, message)

    def begin_parsing(self, parser):
        self.parser = parser

    def end_parsing(self):
        self.parser = None

    def begin_object(self):
        raise NotImplementedError()

    def end_object(self):
        raise NotImplementedError()

    def begin_object_item(self, key, key_quoted):
        raise NotImplementedError()

    def begin_array(self):
        raise NotImplementedError()

    def end_array(self):
        raise NotImplementedError()

    def literal(self, literal, literal_quoted):
        raise NotImplementedError()
