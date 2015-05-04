from unittest import TestCase
from jsoncfg.config_classes import ValueNotFoundNode, ConfigJSONScalar, ConfigJSONObject,\
    ConfigJSONArray, JSONConfigNodeTypeError, ConfigNode, JSONConfigIndexError
from jsoncfg import JSONConfigValueNotFoundError, JSONParserParams, JSONValueMapper
from jsoncfg import loads_config, node_location, node_exists, node_is_object, node_is_array,\
    node_is_scalar, ensure_exists, expect_object, expect_array, expect_scalar

from .utils import WrapCallable


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


class TestValueNotFoundNode(TestCase):
    def test_len(self):
        config = loads_config('{}')
        not_found_node = config.woof
        self.assertIsInstance(not_found_node, ValueNotFoundNode)
        self.assertRaises(JSONConfigValueNotFoundError, lambda: len(not_found_node))

    def test_iter(self):
        config = loads_config('{}')
        not_found_node = config.woof
        self.assertIsInstance(not_found_node, ValueNotFoundNode)
        self.assertRaises(JSONConfigValueNotFoundError, lambda: iter(not_found_node))

    def test_indexing(self):
        config = loads_config('{}')
        not_found_node = config.woof
        self.assertIsInstance(not_found_node, ValueNotFoundNode)
        case0 = not_found_node[100][100]
        self.assertRaises(JSONConfigValueNotFoundError, case0)
        case1 = not_found_node['a']['b']
        self.assertRaises(JSONConfigValueNotFoundError, case1)


class TestJSONValueMapper(TestCase):
    def test_call(self):
        self.assertRaises(NotImplementedError, JSONValueMapper(), None)


class TestConfigNode(TestCase):
    def test_value_fetch(self):
        config = loads_config('{a:0, b:{}, c:[]}')
        scalar = config.a
        obj = config.b
        array = config.c
        not_found = config.d

        self.assertIsInstance(scalar, ConfigJSONScalar)
        self.assertIsInstance(obj, ConfigJSONObject)
        self.assertIsInstance(array, ConfigJSONArray)
        self.assertIsInstance(not_found, ValueNotFoundNode)

        default = object()
        self.assertEqual(scalar(default), 0)
        self.assertEqual(obj(default), {})
        self.assertEqual(array(default), [])
        self.assertEqual(not_found(default), default)

    def test_value_fetch_not_json_value_mapper_instance(self):
        config = loads_config('{a:0}')
        self.assertRaisesRegexp(TypeError, r'1 isn\'t a JSONValueMapper instance!',
                                WrapCallable(config.a), 0, 1)

    def test_unimplemented_fetch_unwrapped_value(self):
        self.assertRaises(NotImplementedError, ConfigNode(0, 0)._fetch_unwrapped_value)


class TestConfigJSONScalar(TestCase):
    def test_len(self):
        config = loads_config('[0]', parser_params=JSONParserParams(root_is_array=True))
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to access the __len__ of a scalar config object\.',
            len,
            config[0],
        )

    def test_iter(self):
        config = loads_config('[0]', parser_params=JSONParserParams(root_is_array=True))
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to iterate a scalar value\.',
            iter,
            config[0],
        )

    def test_contains(self):
        config = loads_config('[0]', parser_params=JSONParserParams(root_is_array=True))
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to access the __contains__ magic method of a scalar config object\.',
            config[0].__contains__,
            0,
        )

    def test_getattr(self):
        config = loads_config('[0]', parser_params=JSONParserParams(root_is_array=True))
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to get an item from a scalar as if it was an object\.',
            config[0].__getattr__,
            'woof',
        )

    def test_getitem(self):
        config = loads_config('[0]', parser_params=JSONParserParams(root_is_array=True))
        self.assertRaisesRegexp(
            TypeError,
            r'You are allowed to index only with string or integer\.',
            config[0].__getitem__,
            None,
        )
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to index into a scalar as if it was an array\.',
            config[0].__getitem__,
            0,
        )
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to get an item from a scalar as if it was an object\.',
            config[0].__getitem__,
            'item',
        )

    def test_repr(self):
        config = loads_config('[0]', parser_params=JSONParserParams(root_is_array=True))
        repr(config[0])


class TestConfigJSONObject(TestCase):
    def test_len(self):
        config = loads_config('{k0:0, k1:1}')
        self.assertEqual(len(config), 2)

    def test_iter(self):
        config = loads_config('{k0:0, k1:1}')
        result = {k: v() for k, v in config}
        self.assertDictEqual(result, {'k0': 0, 'k1': 1})

    def test_contains(self):
        config = loads_config('{k0:0}')
        self.assertTrue('k0' in config)
        self.assertFalse('k1' in config)

    def test_getitem(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to index into an object as if it was an array\.',
            config.__getitem__,
            0,
        )
        self.assertRaisesRegexp(
            TypeError,
            r'You are allowed to index only with string or integer\.',
            config.__getitem__,
            None,
        )
        self.assertIsInstance(config.not_found, ValueNotFoundNode)

    def test_item_not_found(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertRaises(JSONConfigValueNotFoundError, config.nonexistent)

    def test_repr(self):
        config = loads_config(TEST_JSON_STRING)
        repr(config)


class TestConfigJSONArray(TestCase):
    @staticmethod
    def loads_array_config(json_string):
        return loads_config(json_string, JSONParserParams(root_is_array=True))

    def test_len(self):
        config = self.loads_array_config('[0, 1]')
        self.assertEqual(len(config), 2)

    def test_iter(self):
        config = self.loads_array_config('[0, 1]')
        items = set(config_val() for config_val in config)
        self.assertSetEqual(items, {0, 1})

    def test_contains(self):
        config = self.loads_array_config('[]')
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to access the __contains__ magic method of an array\.',
            config.__contains__,
            0,
        )

    def test_getattr(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to get an item from an array as if it was an object\.',
            config.array.__getattr__,
            'item',
        )

    def test_getitem(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertEquals(config.array[0].a(), 0)
        self.assertEquals(config.array[1].b(), 1)
        self.assertRaisesRegexp(
            TypeError,
            r'You are allowed to index only with string or integer\.',
            config.array.__getitem__,
            None,
        )
        self.assertRaisesRegexp(
            JSONConfigNodeTypeError,
            r'You are trying to get an item from an array as if it was an object\.',
            config.array.__getitem__,
            'item',
        )

    def test_getitem_with_negative_index(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertDictEqual(config.array[-1](), {'b': 1})
        self.assertDictEqual(config.array[-2](), {'a': 0})
        self.assertRaises(
            JSONConfigIndexError,
            config.array.__getitem__,
            -3,
        )
        self.assertRaises(
            JSONConfigIndexError,
            config.array.__getitem__,
            2,
        )

    def test_repr(self):
        config = loads_config(TEST_JSON_STRING)
        repr(config.array)


class TestUtilityFunctions(TestCase):
    def test_node_location(self):
        config = loads_config('{k0:0}')
        location = node_location(config)
        self.assertEquals(location, (0, 0))

    def test_node_location_with_value_not_found_node(self):
        config = loads_config('{}')
        self.assertRaises(JSONConfigValueNotFoundError, node_location, config.a)

    def test_node_location_with_invalid_value(self):
        self.assertRaisesRegexp(TypeError, r'Expected a config node but received a list instance.',
                                node_location, [])

    def test_node_exists(self):
        config = loads_config('{k0:0}')
        self.assertTrue(node_exists(config))
        self.assertTrue(node_exists(config.k0))
        self.assertFalse(node_exists(config.not_found))

    def test_node_is_object(self):
        config = loads_config('{k0:0}')
        self.assertTrue(node_is_object(config))
        self.assertFalse(node_is_object(config.k0))
        self.assertFalse(node_is_object(config.not_found))

    def test_node_is_array(self):
        config = loads_config('{a:[0]}')
        self.assertTrue(node_is_array(config.a))
        self.assertFalse(node_is_array(config.a[0]))
        self.assertFalse(node_is_array(config.not_found))

    def test_node_is_scalar(self):
        config = loads_config('{a:[0]}')
        self.assertFalse(node_is_scalar(config.a))
        self.assertTrue(node_is_scalar(config.a[0]))
        self.assertFalse(node_is_scalar(config.not_found))

    def test_ensure_exists(self):
        config = loads_config('{}')
        self.assertIs(config, ensure_exists(config))
        self.assertRaises(JSONConfigValueNotFoundError, ensure_exists, config.a)
        self.assertRaises(TypeError, ensure_exists, None)

    def test_expect_object(self):
        config = loads_config('{a:0}')
        self.assertIs(config, expect_object(config))
        self.assertRaises(JSONConfigValueNotFoundError, expect_object, config.b)
        self.assertRaises(JSONConfigNodeTypeError, expect_object, config.a)
        self.assertRaises(TypeError, expect_object, None)

    def test_expect_array(self):
        config = loads_config('{a:[0]}')
        self.assertIs(config.a, expect_array(config.a))
        self.assertRaises(JSONConfigValueNotFoundError, expect_array, config.not_found)
        self.assertRaises(JSONConfigNodeTypeError, expect_array, config.a[0])
        self.assertRaises(TypeError, expect_array, None)

    def test_expect_scalar(self):
        config = loads_config('{a:[0]}')
        self.assertIs(config.a[0], expect_scalar(config.a[0]))
        self.assertRaises(JSONConfigValueNotFoundError, expect_scalar, config.not_found)
        self.assertRaises(JSONConfigNodeTypeError, expect_scalar, config)
        self.assertRaises(TypeError, expect_scalar, None)
