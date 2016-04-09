from unittest import TestCase
from mock import patch

from jsoncfg import load, load_config, loads, loads_config, JSONConfigParserException,\
    JSONParserParams, StringToScalarConverter, get_python_object_builder_params


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
        lst = loads('[0, 1, 2]', JSONParserParams(root_is_array=True))
        self.assertListEqual(lst, [0, 1, 2])

    def test_invalid_json_scalar(self):
        self.assertRaisesRegexp(JSONConfigParserException, r'Invalid json scalar: "invalid_scalar"',
                                loads, '{key:invalid_scalar}')

    def test_duplicate_key(self):
        self.assertRaisesRegexp(JSONConfigParserException, r'Duplicate key: "my_duplicate_key"',
                                loads, '{my_duplicate_key:0,my_duplicate_key:0}')


class TestLoadsConfig(TestCase):
    def test_object_and_standard_json_datatype_loading(self):
        obj = loads_config(TEST_JSON_STRING)
        self.assertDictEqual(obj(), TEST_JSON_VALUE)

    def test_root_is_array(self):
        lst = loads_config('[0, 1, 2]', JSONParserParams(root_is_array=True))
        self.assertListEqual(lst(), [0, 1, 2])

    def test_invalid_json_scalar(self):
        self.assertRaisesRegexp(JSONConfigParserException, r'Invalid json scalar: "invalid_scalar"',
                                loads_config, '{key:invalid_scalar}')

    def test_duplicate_key(self):
        self.assertRaisesRegexp(JSONConfigParserException, r'Duplicate key: "my_duplicate_key"',
                                loads_config, '{my_duplicate_key:0,my_duplicate_key:0}')


class TestFileLoadFunctions(TestCase):
    @patch('jsoncfg.functions.loads', return_value='loads_return_value')
    @patch('jsoncfg.functions.load_utf_text_file', return_value='{k:0}')
    def test_load(self, mock_load_utf_text_file, mock_loads):
        res = load('filename')
        self.assertEqual(res, 'loads_return_value')
        mock_loads.assert_called_with('{k:0}')
        mock_load_utf_text_file.assert_called_with(
            'filename',
            default_encoding='UTF-8',
            use_utf8_strings=True,
        )

    @patch('jsoncfg.functions.loads_config', return_value='loads_config_return_value')
    @patch('jsoncfg.functions.load_utf_text_file', return_value='{k:0}')
    def test_load_config(self, mock_load_utf_text_file, mock_loads_config):
        res = load_config('filename')
        self.assertEqual(res, 'loads_config_return_value')
        mock_loads_config.assert_called_with('{k:0}')
        mock_load_utf_text_file.assert_called_with(
            'filename',
            default_encoding='UTF-8',
            use_utf8_strings=True,
        )


class TestOther(TestCase):
    def test_custom_const_scalars(self):
        my_const = object()
        my_const2 = object()
        string_to_scalar_converter = StringToScalarConverter(
            scalar_const_literals={'my_const': my_const, 'my_const2': my_const2})
        object_builder_params = get_python_object_builder_params(
            string_to_scalar_converter=string_to_scalar_converter
        )
        res = loads(
            '[my_const, my_const2]',
            parser_params=JSONParserParams(root_is_array=True),
            object_builder_params=object_builder_params,
        )
        self.assertEqual(res, [my_const, my_const2])
