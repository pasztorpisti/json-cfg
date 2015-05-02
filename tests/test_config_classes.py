from unittest import TestCase
from jsoncfg import JSONConfigValueNotFoundError, JSONParserParams
from jsoncfg.config_classes import ValueNotFoundNode, ConfigJSONScalar, ConfigJSONObject,\
    ConfigJSONArray, JSONConfigNodeTypeError
from jsoncfg import loads_config, node_exists, node_is_object, node_is_array, node_is_scalar,\
    ensure_exists, ensure_object, ensure_array, ensure_scalar


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


class TestConfigJSONScalar(TestCase):
    pass


class TestConfigJSONObject(TestCase):
    def test_len(self):
        config = loads_config('{k0:0, k1:1}')
        self.assertEqual(len(config), 2)

    def test_iter(self):
        config = loads_config('{k0:0, k1:1}')
        result = {k: v() for k, v in config}
        self.assertDictEqual(result, {'k0': 0, 'k1': 1})

    def test_in_operator(self):
        config = loads_config('{k0:0}')
        self.assertTrue('k0' in config)
        self.assertFalse('k1' in config)

    def test_getitem(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertTrue(config.true())
        self.assertEqual(config['true'](), True)
        self.assertEqual(config.int(), 5)
        self.assertEqual(config['int'](), 5)

    def test_item_not_found(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertRaises(JSONConfigValueNotFoundError, config.nonexistent[0].blahblah)


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

    def test_getitem(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertEquals(config.array[0].a(), 0)
        self.assertEquals(config.array[1].b(), 1)

    def test_item_not_found(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertRaises(JSONConfigValueNotFoundError, config.array[100].blahblah)


class TestUtilityFunctions(TestCase):
    @staticmethod
    def loads_array_config(json_string):
        return loads_config(json_string, JSONParserParams(root_is_array=True))

    def test_node_exists(self):
        config = loads_config('{k0:0}')
        self.assertTrue(node_exists(config))
        self.assertTrue(node_exists(config.k0))
        self.assertFalse(node_exists(config.k1))

    def test_node_is_object(self):
        config = loads_config('{k0:0}')
        self.assertTrue(node_is_object(config))
        self.assertFalse(node_is_object(config.k0))
        self.assertFalse(node_is_object(config.k1))

    def test_node_is_array(self):
        config = self.loads_array_config('[0]')
        self.assertTrue(node_is_array(config))
        self.assertFalse(node_is_array(config[0]))
        self.assertFalse(node_is_array(config[1]))

    def test_node_is_scalar(self):
        config = self.loads_array_config('[0]')
        self.assertFalse(node_is_scalar(config))
        self.assertTrue(node_is_scalar(config[0]))
        self.assertFalse(node_is_scalar(config[1]))

    def test_ensure_exists(self):
        config = loads_config('{}')
        self.assertIs(config, ensure_exists(config))
        self.assertRaises(JSONConfigValueNotFoundError, ensure_exists, config.a)
        self.assertRaises(ValueError, ensure_exists, None)

    def test_ensure_object(self):
        config = loads_config('{a:0}')
        self.assertIs(config, ensure_object(config))
        self.assertRaises(JSONConfigValueNotFoundError, ensure_object, config.b)
        self.assertRaises(JSONConfigNodeTypeError, ensure_object, config.a)
        self.assertRaises(ValueError, ensure_object, None)

    def test_ensure_array(self):
        config = self.loads_array_config('[0]')
        self.assertIs(config, ensure_array(config))
        self.assertRaises(JSONConfigValueNotFoundError, ensure_array, config[1])
        self.assertRaises(JSONConfigNodeTypeError, ensure_array, config[0])
        self.assertRaises(ValueError, ensure_array, None)

    def test_ensure_scalar(self):
        config = self.loads_array_config('[0]')
        self.assertIs(config[0], ensure_scalar(config[0]))
        self.assertRaises(JSONConfigValueNotFoundError, ensure_scalar, config[1])
        self.assertRaises(JSONConfigNodeTypeError, ensure_scalar, config)
        self.assertRaises(ValueError, ensure_scalar, None)


# TODO: write tests for the mapper parameter of the query fetcher function call
