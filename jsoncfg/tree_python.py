"""
Contains factories to be used with the ObjectBuilderParserListener in order to build
a json tree that consists of pure python objects. With these factories we can load
json objects just like the python standard json.loads() but our parser allows an
extended syntax (unquoted keys, comments, trailing commas).
"""


def default_object_creator(listener):
    obj = {}

    def insert_function(key, value):
        obj[key] = value
    return obj, insert_function


def default_array_creator(listener):
    array = []

    def append_function(item):
        array.append(item)
    return array, append_function


def default_number_converter(number_str):
    is_int = (number_str.startswith('-') and number_str[1:].isdigit()) or number_str.isdigit()
    return int(number_str) if is_int else float(number_str)


class JSONValueConverter(object):
    def __init__(self,
                 number_converter=default_number_converter,
                 json_literals={'null': None, 'true': True, 'false': False}):
        self.number_converter = number_converter
        self.json_literals = json_literals

    _literal_not_found = object()

    def __call__(self, listener, literal, literal_quoted):
        if literal_quoted:
            return literal

        value = self.json_literals.get(literal, self._literal_not_found)
        if value is self._literal_not_found:
            try:
                value = self.number_converter(literal)
            except ValueError:
                listener.error('Invalid json literal: "%s"' % (literal,))
        return value
