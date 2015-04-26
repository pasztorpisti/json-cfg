from unittest import TestCase
from jsonconfig.parser import TextParser, ParserException, ParserListener, JSONParser
from jsonconfig.compatibility import unicode


class TestTextParser(TestCase):
    @staticmethod
    def _text_parser(text):
        parser = TextParser()
        parser.init_text_parser(text)
        return parser

    @staticmethod
    def _skipper(skippable_char):
        def is_skippable(c):
            return c == skippable_char
        return is_skippable

    def test_init(self):
        parser = self._text_parser('abc')
        self.assertEqual(parser.text, 'abc')
        self.assertEqual(parser.pos, 0)
        self.assertEqual(parser.end, 3)
        self.assertEqual(parser.line, 0)
        self.assertEqual(parser.line_pos, 0)

    def test_skip_chars_all(self):
        LEN = 5
        parser = self._text_parser(' ' * LEN)
        parser.skip_chars(parser.end, self._skipper(' '))
        self.assertEqual(parser.pos, LEN)

    def test_skip_chars_none(self):
        parser = self._text_parser('abc')
        parser.skip_chars(parser.end, self._skipper(' '))
        self.assertEqual(parser.pos, 0)

    def test_skip_chars_partial(self):
        parser = self._text_parser(' b')
        parser.skip_chars(parser.end, self._skipper(' '))
        self.assertEqual(parser.pos, 1)

    def test_skip_chars_starting_from_middle(self):
        parser = self._text_parser(' bc')
        parser.skip_chars(parser.end, self._skipper(' '))
        self.assertEqual(parser.pos, 1)
        parser.skip_chars(parser.end, self._skipper(' '))
        self.assertEqual(parser.pos, 1)
        parser.skip_chars(parser.end, self._skipper('b'))
        self.assertEqual(parser.pos, 2)

    def test_skip_to_middle(self):
        parser = self._text_parser('ab')
        parser.skip_to(1)
        self.assertEqual(parser.pos, 1)

    def test_skip_to_end(self):
        parser = self._text_parser('ab')
        parser.skip_to(2)
        self.assertEqual(parser.pos, 2)

    def test_line_counter(self):
        sequence = (
            ('\r', 1),
            (' ',  1),
            ('\n', 2),
            (' ',  2),
            ('\r', 3),
            ('\r', 4),
            (' ',  4),
            ('\n', 5),
            ('\n', 6),
            (' ',  6),
            ('\r', 7),
            ('\n', 7),
            ('\n', 8),
            (' ',  8),
            ('\r', 9),
            ('\r', 10),
            ('\n', 10),
        )
        text, lines = zip(*sequence)
        text = ''.join(text)
        parser = self._text_parser(text)
        line_pos = 0
        for i, line in enumerate(lines):
            parser.skip_to(i+1)
            self.assertEqual(parser.line, line)
            if text[i] != ' ':
                line_pos = i + 1
            self.assertEqual(parser.line_pos, line_pos)

    def test_peek_from_middle_pos(self):
        parser = self._text_parser('abc')
        parser.skip_to(1)
        c = parser.peek(0)
        self.assertEqual(c, 'b')
        c = parser.peek(1)
        self.assertEqual(c, 'c')
        c = parser.peek(2)
        self.assertIsNone(c)
        c = parser.peek(3)
        self.assertIsNone(c)

    def test_peek_from_end_pos(self):
        parser = self._text_parser('abc')
        parser.skip_to(3)
        c = parser.peek(0)
        self.assertIsNone(c)
        c = parser.peek(1)
        self.assertIsNone(c)

    def test_expect_success(self):
        parser = self._text_parser('abc')
        parser.expect('a')
        self.assertEqual(parser.pos, 1)
        parser = self._text_parser('abc')
        parser.skip_to(2)
        parser.expect('c')
        self.assertEqual(parser.pos, 3)

    def test_expect_failure(self):
        parser = self._text_parser('abc')
        self.assertRaises(ParserException, parser.expect, 'b')
        parser = self._text_parser('abc')
        parser.skip_to(3)
        self.assertRaises(ParserException, parser.expect, 'a')


class MyParserListener(ParserListener):
    """
    Parser listener for testing.
    """
    def __init__(self):
        super(MyParserListener, self).__init__()
        self.events = []

    @property
    def event_stream(self):
        return ''.join(self.events)

    def begin_object(self):
        self.events.append('{')

    def end_object(self):
        self.events.append('}')

    def begin_object_item(self, key, key_quoted):
        self.events.append(repr(key))
        self.events.append('q' if key_quoted else 'u')
        self.events.append(':')

    def begin_array(self):
        self.events.append('[')

    def end_array(self):
        self.events.append(']')

    def literal(self, literal, literal_quoted):
        self.events.append(repr(literal))
        self.events.append('q' if literal_quoted else 'u')


class TestJSONParser(TestCase):
    def _test_with_data(self, input_json, expected_event_stream, root_is_array=False, allow_comments=True,
                        allow_unquoted_keys=True, allow_trailing_commas=True):
        listener = MyParserListener()
        parser = JSONParser(
            allow_comments=allow_comments,
            allow_unquoted_keys=allow_unquoted_keys,
            allow_trailing_commas=allow_trailing_commas,
        )
        parser.parse(input_json, listener, root_is_array)
        self.assertEqual(listener.event_stream, expected_event_stream)

    def _assert_raises_regexp(self, regexp, json_str, root_is_array=False, allow_comments=True,
                              allow_unquoted_keys=True, allow_trailing_commas=True):
        listener = MyParserListener()
        parser = JSONParser(
            allow_comments=allow_comments,
            allow_unquoted_keys=allow_unquoted_keys,
            allow_trailing_commas=allow_trailing_commas,
        )
        self.assertRaisesRegexp(ParserException, regexp, parser.parse, json_str, listener, root_is_array)

    def test_root_is_array(self):
        self._assert_raises_regexp('The root of the json is expected to be an array!', '{}', True)
        self._assert_raises_regexp('The root of the json is expected to be an object!', '[]', False)

        self._test_with_data('{}', '{}', False)
        self._test_with_data('[]', '[]', True)

    def test_parse_error_at_beginning(self):
        self._assert_raises_regexp('The json string should start with "\["', 'x', True)
        self._assert_raises_regexp('The json string should start with "\{"', 'x', False)

    def test_garbage_after_json_string(self):
        self._assert_raises_regexp('The json string should start with "\["', 'x', True)
        self._assert_raises_regexp('The json string should start with "\{"', 'x', False)

    def test_basic(self):
        json_string = ' { cfg : asdf, "asdf" : [ 0 , null , /* comment */ [ ] ,\t\r\n // singleline\n { } ] , ggg : { } } '
        expected_events = "{'cfg'u:'asdf'u'asdf'q:['0'u'null'u[]{}]'ggg'u:{}}"
        self._test_with_data(json_string, expected_events)
        self._test_with_data(json_string.replace(' ', ''), expected_events)

    def test_array_root(self):
        self._test_with_data('[5,{},null,"ggg",[null,{}]]', "['5'u{}'null'u'ggg'q['null'u{}]]", True)

    def test_trailing_commas(self):
        self._assert_raises_regexp(r'Trailing commas aren\'t enabled for this parser\.',
                                   '{k:[null,]}', allow_trailing_commas=False)
        self._assert_raises_regexp(r'Trailing commas aren\'t enabled for this parser\.',
                                   '{k:[null],}', allow_trailing_commas=False)
        self._test_with_data('{k:[null,]}', "{'k'u:['null'u]}")
        self._test_with_data('{k:[null],}', "{'k'u:['null'u]}")

    def test_unquoted_keys(self):
        self._assert_raises_regexp(r'Unquoted keys arn\'t allowed\.', '{key:null}', allow_unquoted_keys=False)
        self._test_with_data('{key:null}', "{'key'u:'null'u}")

    def test_comments(self):
        expected = "{'key'u:'null'u}"
        self._test_with_data('{key/**/:null}//', expected)
        self._test_with_data('/*comment*///singleline\n{key://singleline\r//\nnull//singleline\n\r}', expected)
        self._test_with_data('///*\n{key:null}//', expected)
        self._test_with_data('/*//*/{key:null}//', expected)
        self._test_with_data('{key:null}//asdf', expected)
        self._assert_raises_regexp(r'Multiline comment isn\'t closed\.', '/*')

    def test_simple_string_escape_sequences(self):
        self._test_with_data(r'["xxx\\\/\"\b\f\t\r\nyyy"]', '[' + repr('xxx\\/\"\b\f\t\r\nyyy') + 'q]',
                             root_is_array=True)
        self._assert_raises_regexp(r'Quoted string contains an invalid escape sequence\.',
                                   r'["\k"]', root_is_array=True)

    def test_unicode_escape_sequence(self):
        self._test_with_data(unicode(r'["XXX\u1234\u5678WWW\u9abcYYY"]'), u'[' + repr(u'XXX\u1234\u5678WWW\u9abcYYY') + u'q]',
                             root_is_array=True)

    def test_control_character_in_quoted_string(self):
        self._assert_raises_regexp(r'Encountered a control character that isn\'t allowed in quoted strings\.',
                                   '["\n"]', root_is_array=True)
