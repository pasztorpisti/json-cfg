from .parser import JSONParser
from .listener import ObjectBuilderParserListener, default_object_creator, default_array_creator, JSONValueConverter


def loads(s,
          root_is_list=False,
          allow_comments=True,
          allow_unquoted_keys=True,
          allow_trailing_commas=True,
          object_creator=default_object_creator,
          array_creator=default_array_creator,
          value_converter=JSONValueConverter()):
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
    parser.parse(s, listener, root_is_list)
    return listener.object


def load(filename, *args, **kwargs):
    with open(filename) as f:
        json_str = f.read()
    return loads(json_str, *args, **kwargs)
