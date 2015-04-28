from .exceptions import JSONConfigException
import numbers


_undefined = object()


class JSONConfigQueryError(JSONConfigException):
    """
    The base class of every exceptions thrown by this library during config queries.
    """
    def __init__(self, config_node, message):
        message += ' [line=%s;col=%s]' % (config_node.line+1, config_node.column+1)
        super(JSONConfigQueryError, self).__init__(message)
        self.config_node = config_node


class JSONConfigValueConverterError(JSONConfigQueryError):
    def __init__(self, config_node, converter_exception):
        super(JSONConfigValueConverterError, self).__init__(config_node, 'Error converting config value: ' +
                                                            converter_exception.message)
        self.converter_exception = converter_exception


class JSONConfigValueNotFoundError(JSONConfigQueryError):
    def __init__(self, value_not_found):
        self.value_not_found = value_not_found
        path = []
        for component in value_not_found.missing_query_path:
            if isinstance(component, numbers.Integral):
                path.append('[%s]' % component)
            else:
                path.append('.' + component)
        self.relative_path = ''.join(path)
        message = 'Required config value not found. relative path: ' + self.relative_path
        super(JSONConfigValueNotFoundError, self).__init__(value_not_found.parent_config_node, message)


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
    def __init__(self, line, column):
        super(_ConfigNode, self).__init__()
        self.line = line
        self.column = column

    def __call__(self, default=_undefined, mapper=_undefined):
        value = self._fetch_unwrapped_value()
        if mapper is not _undefined:
            try:
                value = mapper(value)
            except Exception as e:
                raise JSONConfigValueConverterError(self, e)
        return value

    def _fetch_unwrapped_value(self):
        raise NotImplementedError()


class ConfigJSONValue(_ConfigNode):
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
        return iter(self._dict)

    def __repr__(self):
        return '%s(len=%r, line=%r, column=%r)' % (self.__class__.__name__,
                                                   len(self), self.line, self.column)

    def _fetch_unwrapped_value(self):
        return {key: node._fetch_unwrapped_value() for key, node in self._dict.items()}

    def _insert(self, key, value):
        self._dict[key] = value


class ConfigJSONArray(_ConfigNode):
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
