# -*- coding: utf-8 -*-

from .exceptions import JSONConfigException
from .parser import ParserException
from .config_classes import JSONConfigQueryError, JSONConfigValueMapperError,\
    JSONConfigValueNotFoundError, JSONConfigNodeTypeError, node_location,\
    node_exists, node_is_object, node_is_array, node_is_scalar,\
    ensure_exists, expect_object, expect_array, expect_scalar
from .functions import loads, load, loads_config, load_config, get_python_object_builder_params,\
    JSONParserParams, ObjectBuilderParams
from .tree_python import DefaultObjectCreator, DefaultArrayCreator, default_number_converter,\
    StringToScalarConverter

__all__ = [
    'JSONConfigException',
    'ParserException',
    'JSONConfigQueryError', 'JSONConfigValueMapperError',
    'JSONConfigValueNotFoundError', 'JSONConfigNodeTypeError', 'node_location',
    'node_exists', 'node_is_object', 'node_is_array', 'node_is_scalar',
    'ensure_exists', 'expect_object', 'expect_array', 'expect_scalar',
    'loads', 'load', 'loads_config', 'load_config', 'get_python_object_builder_params',
    'JSONParserParams', 'ObjectBuilderParams',
    'DefaultObjectCreator', 'DefaultArrayCreator', 'default_number_converter',
    'StringToScalarConverter',
]

# version_info[0]: Increase in case of large milestones/releases.
# version_info[1]: Increase this and zero out version_info[2] if you have explicitly modified
#                  a previously existing behavior/interface.
#                  If the behavior of an existing feature changes as a result of a bugfix
#                  and the new (bugfixed) behavior is that meets the expectations of the
#                  previous interface documentation then you shouldn't increase this, in that
#                  case increase only version_info[2].
# version_info[2]: Increase in case of bugfixes. Also use this if you added new features
#                  without modifying the behavior of the previously existing ones.
version_info = (0, 2, 0)
__version__ = '.'.join(str(n) for n in version_info)
__author__ = 'István Pásztor'
__license__ = 'MIT'
