from unittest import TestCase
from jsoncfg.parser import TextParser, ParserException, ParserListener, JSONParser, JSONParserParams
from jsoncfg.compatibility import my_unicode


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

    def test_skip_chars_all(self):
        parser = self._text_parser(' ' * 5)
        parser.skip_chars(parser.end, self._skipper(' '))
        self.assertEqual(parser.pos, 5)

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
        for i, line in enumerate(lines):
            parser.skip_to(i+1)
            self.assertEqual(parser.line, line)

    def test_column(self):
        parser = TextParser(tab_size=4)
        sequence = (
            ('\t',  4),
            (' ',   5),
            ('\t',  8),
            (' ',   9),
            (' ',  10),
            ('\t', 12),
            (' ',  13),
            (' ',  14),
            (' ',  15),
            ('\t', 16),
            (' ',  17),
            (' ',  18),
            (' ',  19),
            (' ',  20),
            ('\t', 24),
            ('\n',  0),
            ('\t',  4),
            (' ',   5),
            ('\t',  8),
            ('\r',  0),
            ('\n',  0),
            ('\t',  4),
            (' ',   5),
            ('\t',  8),
        )
        text, columns = zip(*sequence)
        text = ''.join(text)
        parser.init_text_parser(text)
        for i, column in enumerate(columns):
            parser.skip_to(i+1)
            self.assertEqual(parser.column, column)

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

    def scalar(self, scalar_str, scalar_str_quoted):
        self.events.append(repr(scalar_str))
        self.events.append('q' if scalar_str_quoted else 'u')


class TestJSONParser(TestCase):
    def _test_with_data(self, input_json, expected_event_stream, root_is_array=False):
        listener = MyParserListener()
        parser = JSONParser(JSONParserParams(root_is_array=root_is_array))
        parser.parse(input_json, listener)
        self.assertEqual(listener.event_stream, expected_event_stream)

    def _assert_raises_regexp(self, regexp, json_str, root_is_array=False,
                              parser_params=JSONParserParams()):
        parser_params.root_is_array = root_is_array
        listener = MyParserListener()
        parser = JSONParser(parser_params)
        self.assertRaisesRegexp(ParserException, regexp, parser.parse, json_str, listener)

    def test_root_is_array(self):
        self._assert_raises_regexp(r'The root of the json is expected to be an array!', '{}', True)
        self._assert_raises_regexp(r'The root of the json is expected to be an object!', '[]',
                                   False)

        self._test_with_data('{}', '{}', False)
        self._test_with_data('[]', '[]', True)

    def test_parse_error_at_beginning(self):
        self._assert_raises_regexp(r'The json string should start with "\["', 'x', True)
        self._assert_raises_regexp(r'The json string should start with "\{"', 'x', False)

    def test_garbage_after_json_string(self):
        self._assert_raises_regexp(r'The json string should start with "\["', 'x', True)
        self._assert_raises_regexp(r'The json string should start with "\{"', 'x', False)

    def test_basic(self):
        json_string = ' { cfg : asdf, "asdf" : [ 0 , null , /* comment */ [ ] ,\t\r\n //'\
                      ' singleline\n { } ] , ggg : { } } '
        expected_events = "{'cfg'u:'asdf'u'asdf'q:['0'u'null'u[]{}]'ggg'u:{}}"
        self._test_with_data(json_string, expected_events)
        self._test_with_data(json_string.replace(' ', ''), expected_events)

    def test_array_root(self):
        self._test_with_data('[5,{},null,"ggg",[null,{}]]', "['5'u{}'null'u'ggg'q['null'u{}]]",
                             True)

    def test_trailing_commas(self):
        self._assert_raises_regexp(r'Trailing commas aren\'t enabled for this parser\.',
                                   '{k:[null,]}',
                                   parser_params=JSONParserParams(allow_trailing_commas=False))
        self._assert_raises_regexp(r'Trailing commas aren\'t enabled for this parser\.',
                                   '{k:[null],}',
                                   parser_params=JSONParserParams(allow_trailing_commas=False))
        self._test_with_data('{k:[null,]}', "{'k'u:['null'u]}")
        self._test_with_data('{k:[null],}', "{'k'u:['null'u]}")

    def test_unquoted_keys(self):
        self._assert_raises_regexp(r'Unquoted keys arn\'t allowed\.', '{key:null}',
                                   parser_params=JSONParserParams(allow_unquoted_keys=False))
        self._test_with_data('{key:null}', "{'key'u:'null'u}")

    def test_comments(self):
        expected = "{'key'u:'null'u}"
        self._test_with_data('{key/**/:null}//', expected)
        self._test_with_data('/*comment*///singleline\n{key://singleline\r//\nnull//'
                             'singleline\n\r}', expected)
        self._test_with_data('///*\n{key:null}//', expected)
        self._test_with_data('/*//*/{key:null}//', expected)
        self._test_with_data('{key:null}//asdf', expected)
        self._assert_raises_regexp(r'Multiline comment isn\'t closed\.', '/*')

    def test_simple_string_escape_sequences(self):
        self._test_with_data(r'["xxx\\\/\"\b\f\t\r\nyyy"]', '[' + repr('xxx\\/\"\b\f\t\r\nyyy') +
                             'q]', root_is_array=True)
        self._assert_raises_regexp(r'Quoted string contains an invalid escape sequence\.',
                                   r'["\k"]', root_is_array=True)

    def test_unicode_escape_sequence(self):
        self._test_with_data(my_unicode(r'["XXX\u1234\u5678WWW\u9abcYYY"]'),
                             u'[' + repr(u'XXX\u1234\u5678WWW\u9abcYYY') + u'q]',
                             root_is_array=True)

    def _perform_surrogate_test(self, escaped_json_string, decoded_python_string):
        self._test_with_data(my_unicode('["' + escaped_json_string + '"]'),
                             u'[' + repr(decoded_python_string) + u'q]',
                             root_is_array=True)

    def test_surrogate_pair_code_point_calculation(self):
        self._perform_surrogate_test(r'WWW\ud800\udc00XXX\ud900\ude80YYY\udbff\udfffZZZ',
                                     u'WWW\U00010000XXX\U00050280YYY\U0010ffffZZZ')

    def test_lone_surrogates(self):
        self._perform_surrogate_test(r'XXX\ud800YYY\udc00ZZZ',
                                     u'XXX\ud800YYY\udc00ZZZ')

    def test_high_low_surrogate_sequences(self):
        # Testing the decoding of 4 subsequent surrogates. Each of the 4 surrogates
        # can be either low or high surrogate so this leads to 2^4 == 16 cases.
        cases = [
            # zero bit means low surrogate, set bit means high surrogate
            (0b0000, u'\udc00\udc00\udc00\udc00'),
            (0b0001, u'\udc00\udc00\udc00\ud800'),
            (0b0010, u'\udc00\udc00\U00010000'),
            (0b0011, u'\udc00\udc00\ud800\ud800'),

            (0b0100, u'\udc00\U00010000\udc00'),
            (0b0101, u'\udc00\U00010000\ud800'),
            (0b0110, u'\udc00\ud800\U00010000'),
            (0b0111, u'\udc00\ud800\ud800\ud800'),

            (0b1000, u'\U00010000\udc00\udc00'),
            (0b1001, u'\U00010000\udc00\ud800'),
            (0b1010, u'\U00010000\U00010000'),
            (0b1011, u'\U00010000\ud800\ud800'),

            (0b1100, u'\ud800\U00010000\udc00'),
            (0b1101, u'\ud800\U00010000\ud800'),
            (0b1110, u'\ud800\ud800\U00010000'),
            (0b1111, u'\ud800\ud800\ud800\ud800'),
        ]

        for mask, decoded_python_string in cases:
            # print('Mask: ' + bin(mask))
            escaped_json_string = ''
            for bit in (0b1000, 0b0100, 0b0010, 0b0001):
                escaped_json_string += r'\ud800' if bit & mask else r'\udc00'
            self._perform_surrogate_test(escaped_json_string, decoded_python_string)

    def test_control_character_in_quoted_string(self):
        self._assert_raises_regexp(r'Encountered a control character that isn\'t allowed in'
                                   ' quoted strings\.', '["\n"]', root_is_array=True)


class TestJSONParserParams(TestCase):
    def test_unexpected_keyword_arguments(self):
        self.assertRaisesRegexp(RuntimeError, r'Unexpected keyword arguments: ',
                                JSONParserParams, my_unexpected_kwarg='woofwoof')


class TestParserListener(TestCase):
    def setUp(self):
        self.parser = JSONParser()
        self.listener = ParserListener()
        self.listener.begin_parsing(self.parser)

    def tearDown(self):
        self.listener.end_parsing()

    def test_begin_end_parsing(self):
        parser = JSONParser()
        listener = ParserListener()
        self.assertIsNone(listener.parser)
        listener.begin_parsing(parser)
        self.assertEqual(listener.parser, parser)
        listener.end_parsing()
        self.assertIsNone(listener.parser)

    def test_begin_object(self):
        self.assertRaises(NotImplementedError, self.listener.begin_object)

    def test_end_object(self):
        self.assertRaises(NotImplementedError, self.listener.end_object)

    def test_begin_object_item(self):
        self.assertRaises(NotImplementedError, self.listener.begin_object_item, 'key', False)

    def test_begin_array(self):
        self.assertRaises(NotImplementedError, self.listener.begin_array)

    def test_end_array(self):
        self.assertRaises(NotImplementedError, self.listener.end_array)

    def test_scalar(self):
        self.assertRaises(NotImplementedError, self.listener.scalar, 'scalar_str', False)

    def test_error(self):
        self.assertRaises(ParserException, self.listener.error, 'test_error_message')
