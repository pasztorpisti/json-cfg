from unittest import TestCase

from jsoncfg import loads_config, JSONConfigValueMapperError
from jsoncfg.value_mappers import *


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


class TestRequireTypeMappers(TestCase):
    def test_require_null(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertIsNone(config.null(require_null))
        self.assertRaises(JSONConfigValueMapperError, config.str, require_null)
        self.assertRaises(JSONConfigValueMapperError, config.str, None, require_null)

    def test_require_bool(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertTrue(config.true(require_bool))
        self.assertRaises(JSONConfigValueMapperError, config.str, require_bool)
        self.assertRaises(JSONConfigValueMapperError, config.str, None, require_bool)

    def test_require_string(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertEqual(config.str(require_string), 'strval')
        self.assertRaises(JSONConfigValueMapperError, config.true, require_string)
        self.assertRaises(JSONConfigValueMapperError, config.true, None, require_string)

    def test_require_number(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertIsInstance(config.int(require_number), int)
        self.assertIsInstance(config.float(require_number), float)
        self.assertRaises(JSONConfigValueMapperError, config.str, require_number)
        self.assertRaises(JSONConfigValueMapperError, config.str, None, require_number)

    def test_require_integer(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertIsInstance(config.int(require_integer), int)
        self.assertRaises(JSONConfigValueMapperError, config.str, require_integer)
        self.assertRaises(JSONConfigValueMapperError, config.str, None, require_integer)

    def test_require_float(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertIsInstance(config.float(require_float), float)
        self.assertRaises(JSONConfigValueMapperError, config.str, require_float)
        self.assertRaises(JSONConfigValueMapperError, config.str, None, require_float)

    def test_require_array(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertIsInstance(config.array(require_array), list)
        self.assertRaises(JSONConfigValueMapperError, config.str, require_array)
        self.assertRaises(JSONConfigValueMapperError, config.str, None, require_array)

    def test_require_object(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertIsInstance(config.obj(require_object), dict)
        self.assertRaises(JSONConfigValueMapperError, config.str, require_object)
        self.assertRaises(JSONConfigValueMapperError, config.str, None, require_object)

    def test_an_arg_is_not_a_type(self):
        self.assertRaisesRegexp(TypeError, 'One of the args you supplied is not a type\.',
                                RequireType, 5)
