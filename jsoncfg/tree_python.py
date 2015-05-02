"""
Contains factories to be used with the ObjectBuilderParserListener in order to build
a json tree that consists of pure python objects. With these factories we can load
json string into python object hierarchies just like the python standard json.loads()
but our parser allows an extended syntax (unquoted keys, comments, trailing commas)
and this parser have other extras, for example you can provide your own dictionary
and list objects.
"""
from collections import OrderedDict


class DefaultObjectCreator(object):
    """
    A factory that creates json objects (dict like objects) when parsing the json
    string into a python object hierarchy.
    """
    def __init__(self, dict_class=OrderedDict):
        """
        :param dict_class: A class that will be instantiated in order to be used as
        a json object in the python object hierarchy. The instances of this class must have
        at least a __setitem__ and a __contains__.
        """
        self.dict_class = dict_class

    def __call__(self, listener, path):
        """
        :param listener: The parser listener that builds the python object hierarchy.
        As an example: the config parser uses listener.parser.line and listener.parser.column
        to get the line/column info for each node of the python object hierarchy.
        """
        obj = self.dict_class()

        def insert_function(key, value):
            obj[key] = value
        return obj, insert_function


class DefaultArrayCreator(object):
    """
    A factory that creates json arrays (list like objects) when parsing the json
    string into a python object hierarchy.
    """
    def __init__(self, list_class=list):
        self.list_class = list_class

    def __call__(self, listener, path):
        """
        :param listener: The parser listener that builds the python object hierarchy.
        As an example: the config parser uses listener.parser.line and listener.parser.column
        to get the line/column info for each node of the python object hierarchy.
        """
        array = self.list_class()

        def append_function(item):
            array.append(item)
        return array, append_function


def default_number_converter(number_str):
    """
    Converts the string representation of a json number into its python object equivalent, an
    int, long, float or whatever type suits.
    """
    is_int = (number_str.startswith('-') and number_str[1:].isdigit()) or number_str.isdigit()
    # FIXME: this handles a wider range of numbers than allowed by the json standard,
    # etc.: float('nan') and float('inf'). But is this a problem?
    return int(number_str) if is_int else float(number_str)


class StringToScalarConverter(object):
    """
    A callable that converts the string representation of json scalars into python objects.
    The JSONParser works only with quoted and non-quoted strings, it doesn't interpret different
    types of json scalars like bool, null, number, string. It is the responsibility of this
    callable to convert the strings (emitted by the parser) into their python equivalent.
    """
    def __init__(self,
                 number_converter=default_number_converter,
                 scalar_const_literals=None):
        """

        :param number_converter: This number converter will be called with every non-quoted
        string that isn't present in the dictionary passed to the scalar_const_literals parameter.
        :param scalar_const_literals: A dictionary that maps non-quoted string representation of
        json scalars to any user supplied python objects.
        If you don't supply this parameter then the default dictionary
        that will be used is {'null': None, 'true': True, 'false': False}. Note that
        you can use this parameter to easily define your own "constants" in the json file.
        """
        self.number_converter = number_converter
        if scalar_const_literals is None:
            self.scalar_const_literals = {'null': None, 'true': True, 'false': False}
        else:
            self.scalar_const_literals = scalar_const_literals

    _not_scalar_const_literal = object()

    def __call__(self, listener, path, scalar_str, scalar_str_quoted):
        """
        :return: After interpreting the string representation of the parsed scalar (scalar_str, and
        scalar_str_quoted) you have to convert it into a python object that will be inserted in the
        object hierarchy.
        """
        if scalar_str_quoted:
            return scalar_str

        value = self.scalar_const_literals.get(scalar_str, self._not_scalar_const_literal)
        if value is self._not_scalar_const_literal:
            try:
                value = self.number_converter(scalar_str)
            except ValueError:
                listener.error('Invalid json scalar: "%s"' % (scalar_str,))
        return value
