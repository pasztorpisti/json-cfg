"""
Contains factories to be used with the ObjectBuilderParserListener in order to build
a json hierarchy that consists of config nodes instead of pure python dict/list/scalar
instances.

Config nodes have the advantage over python objects that they contain line/column numbers
and they provide an easy/automatic way to handle "config querying". A config tree raises
an exception with useful message when a required config value is missing. The exception
message helps to locate the error in the config file (line/column number and sometimes
some other info).
"""


from .config_classes import ConfigJSONObject, ConfigJSONArray, ConfigJSONScalar


def config_object_creator(listener):
    obj = ConfigJSONObject(listener.parser.line, listener.parser.column)
    return obj, obj._insert


def config_array_creator(listener):
    array = ConfigJSONArray(listener.parser.line, listener.parser.column)
    return array, array._append


class ConfigStringToScalarConverter(object):
    """
    A factory that converts the string representation of a json scalar into its python object
    equivalent and then returns it wrapped into a config node.
    """
    def __init__(self, string_to_scalar_converter):
        """
        :param string_to_scalar_converter: A callable that converts the string representation of
        scalars into their python object equivalent.
        """
        self.string_to_scalar_converter = string_to_scalar_converter

    def __call__(self, listener, scalar_str, scalar_str_quoted):
        scalar = self.string_to_scalar_converter(listener, scalar_str, scalar_str_quoted)
        return ConfigJSONScalar(scalar, listener.line, listener.column)
