from unittest import TestCase
from jsoncfg import loads, loads_config, ParserException, JSONParserParams


TEST_JSON_STRING = """
{
    int: 5,
    float: 1.5,
    str: "strval",
    null: null,
    true: true,
    false: false,
    array: [{a:0},{b:1}],
    obj: {},
}
"""

TEST_JSON_VALUE = {
    'int': 5,
    'float': 1.5,
    'str': 'strval',
    'null': None,
    'true': True,
    'false': False,
    'array': [{'a': 0}, {'b': 1}],
    'obj': {},
}


class TestLoads(TestCase):
    def test_object_and_standard_json_datatype_loading(self):
        obj = loads(TEST_JSON_STRING)
        self.assertDictEqual(obj, TEST_JSON_VALUE)

    def test_root_is_array(self):
        lst = loads("[0, 1, 2]", JSONParserParams(root_is_array=True))
        self.assertListEqual(lst, [0, 1, 2])

    def test_invalid_literal(self):
        self.assertRaisesRegexp(ParserException, 'Invalid json literal: "invalid_literal"',
                                loads, '{key:invalid_literal}')

    def test_duplicate_key(self):
        self.assertRaisesRegexp(ParserException, 'Duplicate key: "my_duplicate_key"',
                                loads, '{my_duplicate_key:0,my_duplicate_key:0}')


class TestLoadsConfig(TestCase):
    def test_object_and_standard_json_datatype_loading(self):
        obj = loads_config(TEST_JSON_STRING)
        self.assertDictEqual(obj(), TEST_JSON_VALUE)

    def test_root_is_array(self):
        lst = loads_config("[0, 1, 2]", JSONParserParams(root_is_array=True))
        self.assertListEqual(lst(), [0, 1, 2])

    def test_invalid_literal(self):
        self.assertRaisesRegexp(ParserException, 'Invalid json literal: "invalid_literal"',
                                loads_config, '{key:invalid_literal}')

    def test_duplicate_key(self):
        self.assertRaisesRegexp(ParserException, 'Duplicate key: "my_duplicate_key"',
                                loads_config, '{my_duplicate_key:0,my_duplicate_key:0}')
