"""
Contains the load functions that we use as the public interface of this whole library.
"""

from .parser import JSONParserParams, JSONParser
from .listener import ObjectBuilderParserListener, ObjectBuilderParams
from .tree_python import DefaultObjectCreator, DefaultArrayCreator, JSONValueConverter
from .tree_config import config_object_creator, config_array_creator, ConfigValueConverter


def get_python_object_builder(**kwargs):
    object_creator = kwargs.pop('object_creator', None)
    array_creator = kwargs.pop('array_creator', None)
    value_converter = kwargs.pop('value_converter', None)
    if kwargs:
        raise RuntimeError('Unexpected parameters: %s' % (kwargs,))
    return ObjectBuilderParams(
        object_creator=DefaultObjectCreator() if object_creator is None else object_creator,
        array_creator=DefaultArrayCreator() if array_creator is None else array_creator,
        value_converter=JSONValueConverter() if value_converter is None else value_converter,
    )


def loads(s,
          parser_params=JSONParserParams(),
          object_builder_params=get_python_object_builder()):
    """
    Loads a json string as a python object just like the standard json.loads().
    :param s: The json string to load.
    :params parser_params: Parser parameters.
    :type parser_params: JSONParserParams
    :param object_builder_params: Parameters to the ObjectBuilderParserListener, these parameters
    are mostly factories to create the json object hierarchy while parsing.
    :return: After interpreting the string representation of the parsed value you have to return
    a processed value that will be inserted in the json object hierarchy to be returned by this
    function.
    """
    parser = JSONParser(parser_params)
    listener = ObjectBuilderParserListener(object_builder_params)
    parser.parse(s, listener)
    return listener.result


def load(filename, *args, **kwargs):
    with open(filename) as f:
        json_str = f.read()
    return loads(json_str, *args, **kwargs)


def loads_config(s,
                 parser_params=JSONParserParams(),
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
    parser = JSONParser(parser_params)
    object_builder_params = ObjectBuilderParams(
        object_creator=config_object_creator,
        array_creator=config_array_creator,
        value_converter=ConfigValueConverter(value_converter),
    )
    listener = ObjectBuilderParserListener(object_builder_params)
    parser.parse(s, listener)
    return listener.result


def load_config(filename, *args, **kwargs):
    with open(filename) as f:
        json_str = f.read()
    return loads_config(json_str, *args, **kwargs)
