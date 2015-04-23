from .parser import ParserListener, ParserException


def default_object_creator(parser):
    return {}


def default_array_creator(parser):
    return []


def default_number_converter(number_str):
    return int(number_str) if number_str.isdigit() else float(number_str)


class JSONValueConverter(object):
    def __init__(self,
                 number_converter=default_number_converter,
                 json_literals={'null': None, 'true': True, 'false': False}):
        self.number_converter = number_converter
        self.json_literals = json_literals

    _literal_not_found = object()

    def __call__(self, parser, literal, literal_quoted):
        if literal_quoted:
            return literal

        value = self.json_literals.get(literal, self._literal_not_found)
        if value is self._literal_not_found:
            try:
                value = self.number_converter(literal)
            except ValueError:
                raise ParserException(parser, 'Invalid json literal: "%s"' % (literal,))
        return value


class ObjectBuilderParserListener(ParserListener):
    def __init__(self,
                 object_creator=default_object_creator,
                 array_creator=default_array_creator,
                 value_converter=JSONValueConverter()):
        super(ObjectBuilderParserListener, self).__init__()
        self.object_creator = object_creator
        self.array_creator = array_creator
        self.value_converter = value_converter

        self._object_key = None
        self._container_stack = [(None, None)]
        self._object = None

    @property
    def object(self):
        """ This property holds the parsed object or array after a successful parsing. """
        return self._object

    class ValueType:
        literal = 0
        object = 1
        array = 2

    @property
    def _state(self):
        return self._container_stack[-1]

    def _new_value(self, value):
        container_type, container = self._state
        if container_type == self.ValueType.object:
            container[self._object_key] = value
            self._object_key = None
        elif container_type == self.ValueType.array:
            container.append(value)

    def _pop_container_stack(self):
        if len(self._container_stack) == 2:
            self._object = self._container_stack[-1][1]
        self._container_stack.pop()

    def begin_object(self):
        obj = self.object_creator(self.parser)
        self._new_value(obj)
        self._container_stack.append((self.ValueType.object, obj))

    def end_object(self):
        self._pop_container_stack()

    def begin_object_item(self, key, key_quoted):
        if key in self._state[1]:
            self.error('Duplicate key: "%s"' % (key,))
        self._object_key = key

    def begin_array(self):
        arr = self.array_creator(self.parser)
        self._new_value(arr)
        self._container_stack.append((self.ValueType.array, arr))

    def end_array(self):
        self._pop_container_stack()

    def literal(self, literal, literal_quoted):
        value = self.value_converter(self.parser, literal, literal_quoted)
        self._new_value(value)
