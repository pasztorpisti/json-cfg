"""
Contains factories to be used with the ObjectBuilderParserListener in order to build
a json tree that consists of config nodes instead of pure python dict/list/scalar
instances.

Config nodes have the advantage over python objects that they contain line/column numbers
and they provide an easy/automatic way to handle config querying. A config tree raises
an exception with useful message when a required config value is missing. The exception
message helps to locate the error in the config file (line/column number and sometimes
some other info).
"""


from .configclasses import ConfigJSONObject, ConfigJSONArray, ConfigJSONValue


def config_object_creator(listener):
    obj = ConfigJSONObject(listener.parser.line, listener.parser.column)
    return obj, obj._insert


def config_array_creator(listener):
    array = ConfigJSONArray(listener.parser.line, listener.parser.column)
    return array, array._append


class ConfigValueConverter(object):
    def __init__(self, value_converter):
        self.value_converter = value_converter

    def __call__(self, listener, literal, literal_quoted):
        value = self.value_converter(listener, literal, literal_quoted)
        return ConfigJSONValue(value, listener.line, listener.column)
