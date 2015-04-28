"""
Contains the load functions that we use as the public interface of this whole library.
"""

from .parser import JSONParser
from .listener import ObjectBuilderParserListener
from .tree_python import default_object_creator, default_array_creator, JSONValueConverter
from .tree_config import config_object_creator, config_array_creator, ConfigValueConverter


def loads(s,
          root_is_array=False,
          allow_comments=True,
          allow_unquoted_keys=True,
          allow_trailing_commas=True,
          object_creator=default_object_creator,
          array_creator=default_array_creator,
          value_converter=JSONValueConverter()):
    """
    Loads a json string as a python object just like the standard json.loads().
    :param s: The json string to load.
    :param root_is_array: True: the root of the json hierarchy must be an object/dict.
    False: the root of the json hierarchy must be an array/list.
    :param allow_comments: True: allow single/multi-line comments.
    :param allow_unquoted_keys: Specifying true allows the json object keys to be
    specified without quotes if they don't contain spaces or special characters.
    :param allow_trailing_commas: Allow putting an optional comma after the last
    item in json objects and arrays. Comes handy when you are exchanging lines in
    the config with copy pasting.
    :param object_creator: A callable with signature object_creator(listener) that has to
    return a tuple: (json_object, insert_function). You can access line/column information
    by accessing listener.parser.line and listener.parser.column.
    The returned json_object will be used as a json object (dict) in the hierarchy returned by
    this loads() function. The insert_function(key, value) will be used to insert items.
    Besides this json_object has to support the 'in' operator (by implementing __contains__).
    :param array_creator: A callable with signature array_creator(listener) that has to
    return a tuple: (json_array, append_function).
    The returned json_array will be used as a json array (list) in the hierarchy returned by
    this loads() function. The append_function(item) will be used to add items.
    :param value_converter: This is a callable with signature value_converter(listener, literal, literal_quoted).
    While parsing this function receives every json value that is not an object or an array.
    This includes quoted strings and all other non-quoted stuff (like the null, True, False literals
    and numbers/strings). Note that literal is always a string and literal_quoted is a boolean that
    indicates whether this string was quoted or not in the input json string. The parser interprets
    every value as a quoted or nonquoted string. If literal_quoted is True then literal contains the
    unescaped string value. If literal_quoted is False then it may contain "null", "True" false or
    the string representation of anything else (eg: a number: "1.564") and it's up to you how to
    interpret it. You can define your own literals if you want like interpreting "yes" and "no" as
    boolean values.
    In case of conversion error you should call listener.error() with an error message and this
    raises an exception with information about the error location, etc...
    :return: After interpreting the string representation of the parsed value you have to return
    a processed value that will be inserted in the json object hierarchy to be returned by this
    function.
    """
    parser = JSONParser(
        allow_comments=allow_comments,
        allow_unquoted_keys=allow_unquoted_keys,
        allow_trailing_commas=allow_trailing_commas,
    )
    listener = ObjectBuilderParserListener(
        object_creator=object_creator,
        array_creator=array_creator,
        value_converter=value_converter,
    )
    parser.parse(s, listener, root_is_array)
    return listener.object


def load(filename, *args, **kwargs):
    with open(filename) as f:
        json_str = f.read()
    return loads(json_str, *args, **kwargs)


def loads_config(s,
                 root_is_array=False,
                 allow_comments=True,
                 allow_unquoted_keys=True,
                 allow_trailing_commas=True,
                 value_converter=JSONValueConverter()):
    """
    Works similar to the loads() function but this one returns a json object hierarchy
    that wraps all json objects, arrays and values to provide a nice config query syntax.
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
    parser = JSONParser(
        allow_comments=allow_comments,
        allow_unquoted_keys=allow_unquoted_keys,
        allow_trailing_commas=allow_trailing_commas,
    )
    listener = ObjectBuilderParserListener(
        object_creator=config_object_creator,
        array_creator=config_array_creator,
        value_converter=ConfigValueConverter(value_converter),
    )
    parser.parse(s, listener, root_is_array)
    return listener.object


def load_config(filename, *args, **kwargs):
    with open(filename) as f:
        json_str = f.read()
    return loads_config(json_str, *args, **kwargs)
