"""
Contains the load functions that we use as the public interface of this whole library.
"""

from .parser import JSONParserParams, JSONParser
from .parser_listener import ObjectBuilderParserListener, ObjectBuilderParams
from .tree_python import DefaultObjectCreator, DefaultArrayCreator, StringToScalarConverter
from .tree_config import config_object_creator, config_array_creator, ConfigStringToScalarConverter
from .text_encoding import load_utf_text_file


def get_python_object_builder_params(**kwargs):
    """
    Creates a parameter structure for the ObjectBuilderParserListener. By default
    it initializes all factories so that the parsed object hierarchy will consist
    standard python objects (OrderedDicts, lists, etc...).
    """
    object_creator = kwargs.pop('object_creator', None)
    array_creator = kwargs.pop('array_creator', None)
    string_to_scalar_converter = kwargs.pop('string_to_scalar_converter', None)
    if kwargs:
        raise RuntimeError('Unexpected parameters: %s' % (kwargs,))
    return ObjectBuilderParams(
        object_creator=DefaultObjectCreator() if object_creator is None else object_creator,
        array_creator=DefaultArrayCreator() if array_creator is None else array_creator,
        string_to_scalar_converter=StringToScalarConverter() if string_to_scalar_converter is None
        else string_to_scalar_converter,
    )


def loads(s,
          parser_params=JSONParserParams(),
          object_builder_params=get_python_object_builder_params()):
    """
    Loads a json string as a python object hierarchy just like the standard json.loads(). Unlike
    the standard json.loads() this function uses OrderedDict instances to represent json objects
    but the class of the dictionary to be used is configurable.
    :param s: The json string to load.
    :params parser_params: Parser parameters.
    :type parser_params: JSONParserParams
    :param object_builder_params: Parameters to the ObjectBuilderParserListener, these parameters
    are mostly factories to create the python object hierarchy while parsing.
    """
    parser = JSONParser(parser_params)
    listener = ObjectBuilderParserListener(object_builder_params)
    parser.parse(s, listener)
    return listener.result


def loads_config(s,
                 parser_params=JSONParserParams(),
                 string_to_scalar_converter=StringToScalarConverter()):
    """
    Works similar to the loads() function but this one returns a json object hierarchy
    that wraps all json objects, arrays and scalars to provide a nice config query syntax.
    For example:
    my_config = loads_config(json_string)
    ip_address = my_config.servers.reverse_proxy.ip_address()
    port = my_config.servers.reverse_proxy.port(80)

    Note that the raw unwrapped values can be fetched with the __call__ operator.
    This operator has the following signature: __call__(default=None, mapper=None).
    Fetching a value without specifying a default value means that the value is required
    and it has to be in the config. If it isn't there then a JSONConfigValueNotFoundError
    is raised. The optional mapper parameter can be a function that receives the unwrapped
    value and it can return something that may be based on the input parameter. You can
    also use this mapper parameter to pass a function that performs checking on the
    value and raises an exception (eg. ValueError) on error.

    If you specify a default value and the required config value is not present then
    default is returned. In this case mapper isn't called with the default value.
    """
    parser = JSONParser(parser_params)
    object_builder_params = ObjectBuilderParams(
        object_creator=config_object_creator,
        array_creator=config_array_creator,
        string_to_scalar_converter=ConfigStringToScalarConverter(string_to_scalar_converter),
    )
    listener = ObjectBuilderParserListener(object_builder_params)
    parser.parse(s, listener)
    return listener.result


def load(file_, *args, **kwargs):
    """
    Does exactly the same as loads() but instead of a json string this function
    receives the path to a file containing the json string or a file like object with a read()
    method.
    :param file_: Filename or a file like object with read() method.
    :param default_encoding: The encoding to be used if the file doesn't have a BOM prefix.
    Defaults to UTF-8.
    :param use_utf8_strings: Ignored in case of python3, in case of python2 the default
    value of this is True. True means that the loaded json string should be handled as a utf-8
    encoded str instead of a unicode object.
    """
    json_str = load_utf_text_file(
        file_,
        default_encoding=kwargs.pop('default_encoding', 'UTF-8'),
        use_utf8_strings=kwargs.pop('use_utf8_strings', True),
    )
    return loads(json_str, *args, **kwargs)


def load_config(file_, *args, **kwargs):
    """
    Does exactly the same as loads_config() but instead of a json string this function
    receives the path to a file containing the json string or a file like object with a read()
    method.
    :param file_: Filename or a file like object with read() method.
    :param default_encoding: The encoding to be used if the file doesn't have a BOM prefix.
    Defaults to UTF-8.
    :param use_utf8_strings: Ignored in case of python3, in case of python2 the default
    value of this is True. True means that the loaded json string should be handled as a utf-8
    encoded str instead of a unicode object.
    """
    json_str = load_utf_text_file(
        file_,
        default_encoding=kwargs.pop('default_encoding', 'UTF-8'),
        use_utf8_strings=kwargs.pop('use_utf8_strings', True),
    )
    return loads_config(json_str, *args, **kwargs)
