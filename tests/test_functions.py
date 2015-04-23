from unittest import TestCase
from jsonconfig import ParserException
from jsonconfig.functions import loads


class TestFunctions(TestCase):
    def test_loads_object_and_standard_json_datatype_loading(self):
        obj = loads("""
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
        """)
        self.assertDictEqual(obj, {
            'int': 5,
            'float': 1.5,
            'str': 'strval',
            'null': None,
            'true': True,
            'false': False,
            'array': [{'a': 0}, {'b': 1}],
            'obj': {},
        })

    def test_loads_array(self):
        lst = loads("[0, 1, 2]", root_is_list=True)
        self.assertListEqual(lst, [0, 1, 2])

    def test_loads_invalid_literal(self):
        self.assertRaisesRegexp(ParserException, 'Invalid json literal: "invalid_literal"',
                                loads, '{key:invalid_literal}')

    def test_loads_duplicate_key(self):
        self.assertRaisesRegexp(ParserException, 'Duplicate key: "my_duplicate_key"',
                                loads, '{my_duplicate_key:0,my_duplicate_key:0}')
