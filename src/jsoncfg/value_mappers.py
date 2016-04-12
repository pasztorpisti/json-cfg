import numbers

from .config_classes import JSONValueMapper
from .compatibility import my_basestring


class RequireType(JSONValueMapper):
    def __init__(self, *types):
        for t in types:
            if not isinstance(t, type):
                raise TypeError('One of the args you supplied is not a type.')
        self.types = types

    def __call__(self, json_value):
        if not isinstance(json_value, self.types):
            type_names = ', '.join([t.__name__ for t in self.types])
            raise TypeError('%r isn\'t an instance of any of the following types: %s' %
                            (json_value, type_names))
        return json_value


require_object = require_dict = RequireType(dict)
require_array = require_list = RequireType(list)

require_integer = RequireType(numbers.Integral)
require_float = RequireType(float)
require_number = RequireType(numbers.Number)

require_string = RequireType(my_basestring)
require_bool = RequireType(bool)
require_null = RequireType(type(None))
