# -*- coding: utf-8 -*-

from .exceptions import JSONConfigException
from .parser import ParserException
from .configclasses import JSONConfigQueryError, JSONConfigValueMapperError,\
    JSONConfigValueNotFoundError, JSONConfigNodeTypeError,\
    node_exists, node_is_object, node_is_array, node_is_value,\
    ensure_exists, ensure_object, ensure_array, ensure_value
from .functions import loads, load, loads_config, load_config
from .tree_python import DefaultObjectCreator, default_array_creator, default_number_converter, JSONValueConverter

__all__ = [
    'JSONConfigException',
    'ParserException',
    'JSONConfigQueryError', 'JSONConfigValueMapperError',
    'JSONConfigValueNotFoundError', 'JSONConfigNodeTypeError',
    'node_exists', 'node_is_object', 'node_is_array', 'node_is_value',
    'ensure_exists', 'ensure_object', 'ensure_array', 'ensure_value'
    'loads', 'load', 'loads_config', 'load_config',
    'DefaultObjectCreator', 'default_array_creator', 'default_number_converter', 'JSONValueConverter',
]

# version_info[0]: increase in case of large rewrites that are not backward compatible
# version_info[1]: increase in case of adding new features that keep old ones backward compatible
# version_info[2]: adding only bugfixes without interface modification
version_info = (0, 1, 0)
__version__ = '.'.join(str(n) for n in version_info)
__author__ = 'István Pásztor'
__license__ = 'MIT'
