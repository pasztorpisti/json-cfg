from .exceptions import JSONConfigException
import numbers


_undefined = object()


class JSONConfigQueryError(JSONConfigException):
    """
    The base class of every exceptions thrown by this library during config queries.
    """
    def __init__(self, config_node, message):
        """
        :param config_node: An instance of one of the subclasses of _ConfigNode.
        You can use config_node.line and config_node.column to get the zero based
        line and column number of the error location in the config file.
        """
        message += ' [line=%s;col=%s]' % (config_node.line+1, config_node.column+1)
        super(JSONConfigQueryError, self).__init__(message)
        self.config_node = config_node


class JSONConfigValueMapperError(JSONConfigQueryError):
    """
    This is raised when someone fetches a config value by specifying the "mapper" parameter
    and the mapper function raises an exception. That exception is converted into this one.
    """
    def __init__(self, config_node, mapper_exception):
        """
        :param config_node:  An instance of one of the subclasses of _ConfigNode.
        :param mapper_exception: The exception instance that was raised during value conversion.
        It can be anything...
        """
        super(JSONConfigValueMapperError, self).__init__(config_node, 'Error converting config value: ' +
                                                         mapper_exception.message)
        self.mapper_exception = mapper_exception


class JSONConfigValueNotFoundError(JSONConfigQueryError):
    """
    Raised when the user tries to fetch a value that doesn't exist in the config.
    """
    def __init__(self, value_not_found):
        """
        :param value_not_found: A ValueNotFoundNode instance. Let's say that you query the
        config.servers[1].ip_address() value from the config but the config.servers array
        has only one item. In this case a JSONConfigValueNotFoundError is raised and
        value_not_found.parent_config_node is set to config.servers (that is the last existing
        component from our query path) and self.relative_path will be '[1].ip_address'.
        This way the error location points to the config.servers node and the error message
        says that you wanted to query it with the '[1].ip_address' relative_path that doesn't
        exist.
        """
        self.value_not_found = value_not_found
        path = []
        for component in value_not_found.missing_query_path:
            if isinstance(component, numbers.Integral):
                path.append('[%s]' % component)
            else:
                path.append('.' + component)
        self.relative_path = ''.join(path)
        # TODO: improve the error message: it is possible to do so based on the info we have
        message = 'Required config node not found. Missing query path: %s (relative to error location)' % self.relative_path
        super(JSONConfigValueNotFoundError, self).__init__(value_not_found.parent_config_node, message)


class JSONConfigNodeTypeError(JSONConfigQueryError):
    """
    This error is raised when you try to handle a config node by assuming its type
    to be something else than its actual type. For example you are trying to iterate
    over the key-value pairs of a json array or a simple boolean value or number.
    """
    def __init__(self, config_node, expected_type_name):
        """
        :param expected_type_name: It should be 'json_object', 'json_array' or 'json_value'.
        """
        message = 'Expected a %s but found %s' % (expected_type_name, config_node._json_type)
        super(JSONConfigNodeTypeError, self).__init__(config_node, message)


class ValueNotFoundNode(object):
    def __init__(self, parent_config_node, missing_query_path):
        self.parent_config_node = parent_config_node
        self.missing_query_path = missing_query_path

    def __call__(self, default=_undefined, mapper=_undefined):
        if default is _undefined:
            raise JSONConfigValueNotFoundError(self)
        return default

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, item):
        return ValueNotFoundNode(self.parent_config_node, self.missing_query_path + [item])

    def __len__(self):
        raise JSONConfigValueNotFoundError(self)

    def __iter__(self):
        raise JSONConfigValueNotFoundError(self)


class _ConfigNode(object):
    """
    Base class for the actual classes whose instances build up the config
    object hierarchy wrapping the actual json objects/arrays/values.
    Note that this class and its subclasses should have only private members
    with names that start with '_' because the keys in the json config
    can be accessed using the member operator (dot) and the members of the
    config node class instances should not conflict with the keys in the
    config files.
    """

    # used for error reporting
    _json_type = 'unknown'

    def __init__(self, line, column):
        """
        :param line: Zero based line number. (Add 1 for human readable error reporting).
        :param column: Zero based column number. (Add 1 for human readable error reporting).
        """
        super(_ConfigNode, self).__init__()
        self.line = line
        self.column = column

    def __call__(self, default=_undefined, mapper=_undefined):
        value = self._fetch_unwrapped_value()
        if mapper is not _undefined:
            try:
                value = mapper(value)
            except Exception as e:
                raise JSONConfigValueMapperError(self, e)
        return value

    def _fetch_unwrapped_value(self):
        raise NotImplementedError()


class ConfigJSONValue(_ConfigNode):
    _json_type = 'json_value'

    def __init__(self, value, line, column):
        super(ConfigJSONValue, self).__init__(line, column)
        self.value = value

    def __getattr__(self, item):
        return ValueNotFoundNode(self, [item])

    def __getitem__(self, index):
        return ValueNotFoundNode(self, [index])

    def __len__(self):
        raise JSONConfigValueNotFoundError(self)

    def __iter__(self):
        raise JSONConfigValueNotFoundError(self)

    def __repr__(self):
        return '%s(value=%r, line=%r, column=%r)' % (self.__class__.__name__,
                                                     self.value, self.line, self.column)

    def _fetch_unwrapped_value(self):
        return self.value


class ConfigJSONObject(_ConfigNode):
    _json_type = 'json_object'

    def __init__(self, line, column):
        super(ConfigJSONObject, self).__init__(line, column)
        self._dict = {}

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, item):
        if item in self._dict:
            return self._dict[item]
        return ValueNotFoundNode(self, [item])

    def __contains__(self, item):
        return item in self._dict

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict.items())

    def __repr__(self):
        return '%s(len=%r, line=%r, column=%r)' % (self.__class__.__name__,
                                                   len(self), self.line, self.column)

    def _fetch_unwrapped_value(self):
        return {key: node._fetch_unwrapped_value() for key, node in self._dict.items()}

    def _insert(self, key, value):
        self._dict[key] = value


class ConfigJSONArray(_ConfigNode):
    _json_type = 'json_array'

    def __init__(self, line, column):
        super(ConfigJSONArray, self).__init__(line, column)
        self._list = []

    def __getattr__(self, item):
        return ValueNotFoundNode(self, [item])

    def __getitem__(self, index):
        if isinstance(index, numbers.Integral):
            if index < 0:
                index += len(self._list)
            if 0 <= index < len(self._list):
                return self._list[index]
        return ValueNotFoundNode(self, [index])

    def __len__(self):
        return len(self._list)

    def __iter__(self):
        return iter(self._list)

    def __repr__(self):
        return '%s(len=%r, line=%r, column=%r)' % (self.__class__.__name__,
                                                   len(self), self.line, self.column)

    def _fetch_unwrapped_value(self):
        return [node._fetch_unwrapped_value() for node in self._list]

    def _append(self, item):
        self._list.append(item)


def node_exists(config_node):
    """ Returns True if the specified config node
    refers to an existing config entry. """
    return isinstance(config_node, _ConfigNode)


def node_is_object(config_node):
    """ Returns True if the specified config node refers
    to an existing config entry that is a json object (dict). """
    return isinstance(config_node, ConfigJSONObject)


def node_is_array(config_node):
    """ Returns True if the specified config node refers
    to an existing config entry that is a json array (list). """
    return isinstance(config_node, ConfigJSONArray)


def node_is_value(config_node):
    """ Returns True if the specified config node refers to an existing config
    entry that isn't a json object (dict) or array (list) but something else. """
    return isinstance(config_node, ConfigJSONValue)


def _guarantee_node_class(config_node, node_class):
    if isinstance(config_node, node_class):
        return config_node
    if isinstance(config_node, ValueNotFoundNode):
        raise JSONConfigValueNotFoundError(config_node)
    if isinstance(config_node, _ConfigNode):
        raise JSONConfigNodeTypeError(config_node, node_class._json_type)
    raise ValueError('Expected a %s or %s instance but received %s.' % (
        _ConfigNode.__name__, ValueNotFoundNode.__name__, config_node.__class__.__name__))


# Note: The ensure_*() functions would be quite superfluous after introducing
# a nice json-schema based checking. They would be still useful when someone
# wouldn't like to use schema.


def ensure_exists(config_node):
    return _guarantee_node_class(config_node, _ConfigNode)


def ensure_object(config_node):
    return _guarantee_node_class(config_node, ConfigJSONObject)


def ensure_array(config_node):
    return _guarantee_node_class(config_node, ConfigJSONArray)


def ensure_value(config_node):
    return _guarantee_node_class(config_node, ConfigJSONValue)
