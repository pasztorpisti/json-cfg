from unittest import TestCase
from jsoncfg import JSONConfigValueNotFoundError
from jsoncfg.configclasses import ValueNotFoundNode, ConfigJSONValue, ConfigJSONObject, ConfigJSONArray
from jsoncfg import loads_config


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
        value = config.a
        obj = config.b
        array = config.c
        not_found = config.d

        self.assertIsInstance(value, ConfigJSONValue)
        self.assertIsInstance(obj, ConfigJSONObject)
        self.assertIsInstance(array, ConfigJSONArray)
        self.assertIsInstance(not_found, ValueNotFoundNode)

        default = object()
        self.assertEqual(value(default), 0)
        self.assertEqual(obj(default), {})
        self.assertEqual(array(default), [])
        self.assertEqual(not_found(default), default)


class TestConfigJSONValue(TestCase):
    pass


class TestConfigJSONObject(TestCase):
    def test_len(self):
        config = loads_config('{k0:0, k1:1}')
        self.assertEqual(len(config), 2)

    def test_iter(self):
        config = loads_config('{k0:0, k1:1}')
        keys = set(iter(config))
        self.assertSetEqual(keys, {'k0', 'k1'})

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
    def test_len(self):
        config = loads_config('[0, 1]', root_is_array=True)
        self.assertEqual(len(config), 2)

    def test_iter(self):
        config = loads_config('[0, 1]', root_is_array=True)
        items = set(config_val() for config_val in config)
        self.assertSetEqual(items, {0, 1})

    def test_getitem(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertEquals(config.array[0].a(), 0)
        self.assertEquals(config.array[1].b(), 1)

    def test_item_not_found(self):
        config = loads_config(TEST_JSON_STRING)
        self.assertRaises(JSONConfigValueNotFoundError, config.array[100].blahblah)
