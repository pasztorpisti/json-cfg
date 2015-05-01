from .parser import ParserListener


class ObjectBuilderParams(object):
    def __init__(self, object_creator, array_creator, value_converter):
        """
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
        """
        self.object_creator = object_creator
        self.array_creator = array_creator
        self.value_converter = value_converter


class ObjectBuilderParserListener(ParserListener):
    """ A configurable parser listener implementation that can be configured to
    build a json tree using the user supplied object/array/value factories. """
    def __init__(self, params):
        super(ObjectBuilderParserListener, self).__init__()
        self.params = params

        self._object_key = None
        # The lambda function could actually be a None but that way we get a warning in
        # self._new_value() that the insert_function isn't callable...
        self._container_stack = [(None, None, lambda *args: None)]
        self._result = None

    @property
    def result(self):
        """ This property holds the parsed object or array after a successful parsing. """
        return self._result

    class ContainerType(object):
        object = 0
        array = 1

    @property
    def _state(self):
        return self._container_stack[-1]

    def _new_value(self, value):
        container_type, _, insert_function = self._state
        if container_type == self.ContainerType.object:
            insert_function(self._object_key, value)
            self._object_key = None
        elif container_type == self.ContainerType.array:
            insert_function(value)

    def _pop_container_stack(self):
        if len(self._container_stack) == 2:
            self._result = self._container_stack[-1][1]
        self._container_stack.pop()

    def begin_object(self):
        obj, insert_function = self.params.object_creator(self)
        self._new_value(obj)
        self._container_stack.append((self.ContainerType.object, obj, insert_function))

    def end_object(self):
        self._pop_container_stack()

    def begin_object_item(self, key, key_quoted):
        if key in self._state[1]:
            self.error('Duplicate key: "%s"' % (key,))
        self._object_key = key

    def begin_array(self):
        arr, append_function = self.params.array_creator(self)
        self._new_value(arr)
        self._container_stack.append((self.ContainerType.array, arr, append_function))

    def end_array(self):
        self._pop_container_stack()

    def literal(self, literal, literal_quoted):
        value = self.params.value_converter(self.parser, literal, literal_quoted)
        self._new_value(value)
