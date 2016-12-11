import json

"""
Contains the load functions that we use as the public interface of this whole library.
"""
from .parser import JSONParserParams, JSONParser
from .parser_listener import ObjectBuilderParserListener
from .tree_python import PythonObjectBuilderParams, DefaultStringToScalarConverter
from .tree_config import ConfigObjectBuilderParams
from .text_encoding import load_utf_text_file


def loads(s,
          parser_params=JSONParserParams(),
          object_builder_params=PythonObjectBuilderParams()):
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
                 string_to_scalar_converter=DefaultStringToScalarConverter()):
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
    object_builder_params = ConfigObjectBuilderParams(
        string_to_scalar_converter=string_to_scalar_converter)
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


def save_config(fileName, config):
    with open(fileName, 'w') as fobj:
        fobj.write(config_to_json_str(config))


def config_to_json_str(config):
    json_data = __config_to_json(config)
    return json.dumps(json_data, sort_keys=True,
                      indent=4, separators=(',', ': '))


def __config_to_json(config_json_object):
    jsonData = {}
    for key, value in config_json_object._dict.items():
        if key.startswith('_'):
            continue

        jsonData[key] = __convert_to_json_type(value)

    return jsonData


def __convert_to_json_type(item):
    from .config_classes import ConfigJSONObject, ConfigJSONArray, ConfigJSONScalar

    if isinstance(item, ConfigJSONObject):
        return __config_to_json(item)

    if isinstance(item, ConfigJSONArray):
        return [__convert_to_json_type(i) for i in item]

    if isinstance(item, ConfigJSONScalar):
        return item.value

    return item


class ConfigWithWrapper:
    def __init__(self, config_file_name):
        self.__config = load_config(config_file_name)
        self.__config_file_name = config_file_name

        self.__check_str = None

    def __getattr__(self, item):
        """ For direct usage, with out the with bock """
        if item.startswith('_ConfigWithWrapper__'):
            return getattr(self, item)

        return getattr(self.__config, item)

    def __getitem__(self, item):
        """ For direct usage, with out the with bock """
        return self.__config[item]

    def __setattr__(self, item, value):
        """ For direct usage, with out the with bock """
        if item.startswith('_ConfigWithWrapper__'):
            self.__dict__[item] = value
            return

        setattr(self.__config, item, value)

    def __setitem__(self, item, value):
        """ For direct usage, with out the with bock """
        self.__config[item] = value

    def __call__(self, *args, **kwargs):
        """ For direct usage, with out the with bock """
        return self.__config(*args, **kwargs)

    def __len__(self):
        """ For direct usage, with out the with bock """
        return len(self.__config)

    def __contains__(self, item):
        """ For direct usage, with out the with bock """
        return item in self.__config

    def __enter__(self):
        """ Enter the with bloc

        Store the current state of the config, so we can compare it to see if we need
        to save it.

        """
        self.__check_str = config_to_json_str(self.__config)
        return self.__config

    def __exit__(self, type, value, tb):
        """  Exit the with block

        See if anything has changed, if it has, save it.

        """

        if self.__check_str != config_to_json_str(self.__config):
            save_config(self.__config_file_name, self.__config)
