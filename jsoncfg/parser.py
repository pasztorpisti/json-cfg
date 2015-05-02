"""
This file contains the JSON parser that works like a SAX XML parser.
"""

from .compatibility import my_xrange, my_unichr, my_unicode, utf8chr
from .exceptions import JSONConfigException


class ParserException(JSONConfigException):
    def __init__(self, parser, error_message):
        self.error_message = error_message
        self.line = parser.line + 1
        self.column = parser.column + 1
        message = '%s [line=%s;col=%s]' % (error_message, self.line, self.column)
        super(ParserException, self).__init__(message)


class TextParser(object):
    """
    A base class for parsers. It handles the position in the parsed text and
    tracks the current line/column number.
    """
    def __init__(self, tab_size=4):
        super(TextParser, self).__init__()
        self.tab_size = tab_size
        self.text = None
        self.pos = 0
        self.end = 0
        self.line = 0
        self.prev_newline_char = None
        self._column = 0
        self._column_query_pos = 0

    @property
    def column(self):
        """ Returns the zero based column number based on the
        current position of the parser. """
        for i in my_xrange(self._column_query_pos, self.pos):
            if self.text[i] == '\t':
                self._column += self.tab_size
                self._column -= self._column % self.tab_size
            else:
                self._column += 1
        self._column_query_pos = self.pos
        return self._column

    def init_text_parser(self, text):
        assert self.text is None
        self.text = text
        self.end = len(text)

    def error(self, message):
        """ Raises an exception with the given message and with the current position of
        the parser in the parsed json string. """
        raise ParserException(self, message)

    def skip_chars(self, target_pos, is_char_skippable_func):
        assert self.pos <= target_pos <= self.end
        target_pos = min(target_pos, self.end)
        for self.pos in my_xrange(self.pos, target_pos):
            c = self.text[self.pos]
            if not is_char_skippable_func(c):
                break
            if c in '\r\n':
                if self.prev_newline_char is not None and self.prev_newline_char != c:
                    # this is the second char of a CRLF or LFCR
                    self.prev_newline_char = None
                else:
                    self.prev_newline_char = c
                    self.line += 1
                self._column_query_pos = self.pos + 1
                self._column = 0
            else:
                self.prev_newline_char = None
        else:
            self.pos = target_pos

    def skip_to(self, target_pos):
        """
        Moves the pointer to target_pos (if the current position is less than target_pos)
        and keeps track the current line/column.
        """
        self.skip_chars(target_pos, lambda c: True)

    def skip_char(self):
        """ Skips a single character. """
        self.skip_to(self.pos + 1)

    def peek(self, offset=0):
        """ Looking forward in the input text without actually stepping the current position.
        returns None if the current position is at the end of the input. """
        pos = self.pos + offset
        if pos >= self.end:
            return None
        return self.text[pos]

    def expect(self, c):
        """
        If the current position doesn't hold the specified c character then it raises an
        exception, otherwise it skips the specified character (moves the current position forward).
        """
        if self.peek() != c:
            self.error('Expected "%c"' % (c,))
        self.skip_char()


class JSONParserParams(object):
    def __init__(self, **params):
        """
        :param tab_size: Used when calculating the column of the error location. Defaults to 4.
        :param root_is_array: True: the root of the json hierarchy must be an object/dict.
        False: the root of the json hierarchy must be an array/list.
        :param allow_comments: True: allow single/multi-line comments.
        :param allow_unquoted_keys: Specifying true allows the json object keys to be
        specified without quotes if they don't contain spaces or special characters.
        :param allow_trailing_commas: Allow putting an optional comma after the last
        item in json objects and arrays. Comes handy when you are exchanging lines in
        the config with copy pasting.
        """
        self.tab_size = params.pop('tab_size', 4)
        self.root_is_array = params.pop('root_is_array', False)
        self.allow_comments = params.pop('allow_comments', True)
        self.allow_unquoted_keys = params.pop('allow_unquoted_keys', True)
        self.allow_trailing_commas = params.pop('allow_trailing_commas', True)
        if params:
            raise RuntimeError('Unexpected keyword arguments: %s' % (params,))


class JSONParser(TextParser):
    """
    A simple json parser that works with a fixed sized input buffer (without input streaming) but
    this should not be a problem in case of config files that usually have a small limited size.
    This parser emits events similarly to a SAX XML parser. The user of this class can implement
    several different kind of event listeners. We will work with a listener that builds a json
    object hierarchy but later we could implement for example a json validator listener...
    """
    spaces = set(' \t\r\n')
    special_chars = set('{}[]",:/*')
    spaces_and_special_chars = spaces | special_chars

    def __init__(self, params=JSONParserParams()):
        super(JSONParser, self).__init__(tab_size=params.tab_size)
        self.params = params
        self.listener = None

    def parse(self, json_text, listener):
        """
        Parses the specified json_text and emits parser events to the listener.
        If root_is_array then the root element of the json has to be an array/list,
        otherwise the expected root is a json object/dict.

        In case of python2 the json_text can be either an utf8 encoded string
        or a unicode object and the fired parser events will use the same format.
        """
        listener.begin_parsing(self)
        try:
            self.init_text_parser(json_text)
            self.listener = listener

            c = self._skip_spaces_and_peek()
            if c == '{':
                if self.params.root_is_array:
                    self.error('The root of the json is expected to be an array!')
                self._parse_object()
            elif c == '[':
                if not self.params.root_is_array:
                    self.error('The root of the json is expected to be an object!')
                self._parse_array()
            else:
                self.error('The json string should start with "%s"' % (
                    '[' if self.params.root_is_array else '{'))

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
            if not self.params.allow_comments:
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
        for pos in my_xrange(self.pos, self.end):
            if self.text[pos] in '\r\n':
                self.skip_to(pos + 1)
                break
        else:
            self.skip_to(self.end)

    def _skip_multiline_comment(self):
        for pos in my_xrange(self.pos, self.end-1):
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
                    if not self.params.allow_trailing_commas:
                        self.error('Trailing commas aren\'t enabled for this parser.')
                    self.skip_char()
                    self.listener.end_object()
                    break

            key, key_quoted, pos_after_key = self._parse_and_return_string(
                self.params.allow_unquoted_keys)
            self.listener.begin_object_item(key, key_quoted)
            # We step self.pos and self.line only after a successful call to the listener
            # because in case of an exception that is raised from the listener we want the
            # line/column number to point to the beginning of the parsed string.
            self.skip_to(pos_after_key)

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
                    if not self.params.allow_trailing_commas:
                        self.error('Trailing commas aren\'t enabled for this parser.')
                    self.skip_char()
                    self.listener.end_array()
                    break

            self._parse_value()
            first_item = False

    def _parse_value(self):
        c = self._skip_spaces_and_peek()
        if c == '{':
            self._parse_object()
        elif c == '[':
            self._parse_array()
        else:
            self._parse_scalar()

    def _parse_scalar(self):
        scalar_str, scalar_str_quoted, pos_after_scalar = self._parse_and_return_string(True)
        self.listener.scalar(scalar_str, scalar_str_quoted)
        self.skip_to(pos_after_scalar)

    def _parse_and_return_string(self, allow_unquoted):
        c = self._skip_spaces_and_peek()
        quoted = c == '"'
        if not quoted and not allow_unquoted:
            self.error('Unquoted keys arn\'t allowed.')

        if quoted:
            return self._parse_and_return_quoted_string()
        return self._parse_and_return_unquoted_string()

    def _parse_and_return_unquoted_string(self):
        """
        Parses a string that has no quotation marks so it doesn't
        contain any special characters and we don't have to interpret
        any escape sequences.
        :return: (string, quoted=False, end_of_string_pos)
        """
        begin = self.pos
        for end in my_xrange(self.pos, self.end):
            if self.text[end] in self.spaces_and_special_chars:
                break
        else:
            end = self.end
        if begin == end:
            self.error('Expected a scalar here.')
        return self.text[begin:end], False, end

    def _parse_and_return_quoted_string(self):
        """
        Parses a string that has quotation marks so it may contain
        special characters and escape sequences.
        :return: (unescaped_string, quoted=True, end_of_string_pos)
        """
        result = []
        pos = self.pos + 1
        segment_begin = pos
        my_chr = my_unichr if isinstance(self.text, my_unicode) else utf8chr
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
                    code_point, pos = self._handle_unicode_escape(pos)
                    result.append(my_chr(code_point))
                else:
                    char, pos = self._handle_escape(pos, c)
                    result.append(char)
                segment_begin = pos
            else:
                pos += 1
        return ''.join(result), True, pos

    def _handle_unicode_escape(self, pos):
        if self.end - pos < 5:
            self.error('Reached the end of stream while parsing quoted string.')
        pos += 1
        try:
            code_point = int(self.text[pos:pos+4], 16)
        except ValueError:
            self.skip_to(pos - 2)
            self.error('Error decoding unicode escape sequence.')
        else:
            pos += 4
            if 0xd800 <= code_point < 0xdc00 and self.end-pos >= 6 and\
                    self.text[pos] == '\\' and self.text[pos+1] == 'u':
                try:
                    low_surrogate = int(self.text[pos+2:pos+6], 16)
                except ValueError:
                    self.skip_to(pos)
                    self.error('Error decoding unicode escape sequence.')
                else:
                    if 0xdc00 <= low_surrogate < 0xe000:
                        pos += 6
                        code_point = 0x10000 + (((code_point - 0xd800) << 10) |
                                               (low_surrogate - 0xdc00))
            return code_point, pos

    def _handle_escape(self, pos, c):
        char = {
            '\\': '\\',
            '/': '/',
            '"': '"',
            'b': '\b',
            'f': '\f',
            't': '\t',
            'r': '\r',
            'n': '\n',
        }.get(c)
        if char is None:
            self.skip_to(pos - 1)
            self.error('Quoted string contains an invalid escape sequence.')
        return char, pos + 1


class ParserListener(object):
    """ Base class for parser listeners. """
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

    def scalar(self, scalar, scalar_quoted):
        raise NotImplementedError()
