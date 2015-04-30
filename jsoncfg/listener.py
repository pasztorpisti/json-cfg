from .parser import ParserListener


class ObjectBuilderParserListener(ParserListener):
    """ A configurable parser listener implementation that can be configured to
    build a json tree using the user supplied object/array/value factories. """
    def __init__(self, object_creator, array_creator, value_converter):
        super(ObjectBuilderParserListener, self).__init__()
        self.object_creator = object_creator
        self.array_creator = array_creator
        self.value_converter = value_converter

        self._object_key = None
        # The lambda function could actually be a None but that way we get a warning in
        # self._new_value() that the insert_function isn't callable...
        self._container_stack = [(None, None, lambda *args: None)]
        self._object = None

    @property
    def object(self):
        """ This property holds the parsed object or array after a successful parsing. """
        return self._object

    class ContainerType:
        object = 0
        array = 1

    @property
    def _state(self):
        return self._container_stack[-1]

    def _new_value(self, value):
        container_type, container, insert_function = self._state
        if container_type == self.ContainerType.object:
            insert_function(self._object_key, value)
            self._object_key = None
        elif container_type == self.ContainerType.array:
            insert_function(value)

    def _pop_container_stack(self):
        if len(self._container_stack) == 2:
            self._object = self._container_stack[-1][1]
        self._container_stack.pop()

    def begin_object(self):
        obj, insert_function = self.object_creator(self)
        self._new_value(obj)
        self._container_stack.append((self.ContainerType.object, obj, insert_function))

    def end_object(self):
        self._pop_container_stack()

    def begin_object_item(self, key, key_quoted):
        if key in self._state[1]:
            self.error('Duplicate key: "%s"' % (key,))
        self._object_key = key

    def begin_array(self):
        arr, append_function = self.array_creator(self)
        self._new_value(arr)
        self._container_stack.append((self.ContainerType.array, arr, append_function))

    def end_array(self):
        self._pop_container_stack()

    def literal(self, literal, literal_quoted):
        value = self.value_converter(self.parser, literal, literal_quoted)
        self._new_value(value)
