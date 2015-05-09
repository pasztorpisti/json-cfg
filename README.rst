========
json-cfg
========

.. image:: https://img.shields.io/travis/pasztorpisti/json-cfg.svg?style=flat
    :target: https://travis-ci.org/pasztorpisti/json-cfg
    :alt: build

.. image:: https://img.shields.io/codacy/25854a088e89472f9fbf2bd5c1633834.svg?style=flat
    :target: https://www.codacy.com/app/pasztorpisti/json-cfg
    :alt: code quality

.. image:: https://landscape.io/github/pasztorpisti/json-cfg/master/landscape.svg?style=flat
    :target: https://landscape.io/github/pasztorpisti/json-cfg/master
    :alt: code health

.. image:: https://img.shields.io/coveralls/pasztorpisti/json-cfg/master.svg?style=flat
    :target: https://coveralls.io/r/pasztorpisti/json-cfg?branch=master
    :alt: coverage

.. image:: https://img.shields.io/pypi/v/json-cfg.svg?style=flat
    :target: https://pypi.python.org/pypi/json-cfg
    :alt: pypi

.. image:: https://img.shields.io/github/tag/pasztorpisti/json-cfg.svg?style=flat
    :target: https://github.com/pasztorpisti/json-cfg
    :alt: github

.. image:: https://img.shields.io/github/license/pasztorpisti/json-cfg.svg?style=flat
    :target: https://github.com/pasztorpisti/json-cfg/blob/master/LICENSE.txt
    :alt: license: MIT

.. contents::

------------
Introduction
------------

The goal of this library is providing a json config file loader that has
the following extras compared to the standard `json.load()`:

- A larger subset of javascript (and not some weird/exotic extension to json that
  would turn json into something that has nothing to do with json/javascript):

    - backward compatible with json so you can still load standard json files too
    - single and multi-line comments - this is more useful then you would think:
      it is good not only for documentation but also for temporarily disabling
      a block in your config without actually deleting entries
    - object (dictionary) keys without quotes
    - trailing commas (allowing a comma after the last item of objects and arrays)

- Providing line number information for each element of the loaded config file
  and using this to display useful error messages that help locating errors not
  only while parsing the file but also when processing/interpreting it.
- A simple config query syntax that handles default values, required elements and
  automatically raises an exception in case of error (with useful info including
  the location of the error in the config file).


Config file examples
--------------------

A traditional json config file:

.. code-block:: javascript

    {
        "servers": [
            {
                "ip_address": "127.0.0.1",
                "port": 8080
            },
            {
                "ip_address": "127.0.0.1",
                "port": 8081
            }
        ],
        "superuser_name": "tron"
    }

Something similar but better with json-cfg:

.. code-block:: javascript
    
    {
        // Note that we can get rid of most quotation marks.
        servers: [
            {
                ip_address: "127.0.0.1",
                port: 8080
            },
            // We have commented out the block of the second server below.
            // Trailing commas are allowed so the comma after the
            // first block (above) doesn't cause any problems.
            /*
            {
                ip_address: "127.0.0.1",
                port: 8081
            },  // <-- optional trailing comma
            /**/
        ],
        superuser_name: "tron",  // <-- optional trailing comma
    }

Note that json-cfg can load both config files because standard json is a subset of the extended
syntax allowed by json-cfg.

.. tip::

    Use javascript syntax highlight in your text editor for json config files
    whenever possible - this makes reading config files much easier especially
    when you have a lot of comments or large commented config blocks.

-----
Usage
-----

Installation
------------

.. code-block:: sh

    pip install json-cfg

Alternatively you can download the zipped library from https://pypi.python.org/pypi/json-cfg

Quick-starter
-------------

The json-cfg library provides two modes when it comes to loading config files: One that is very
similar to the standard `json.loads()` and another one that returns the json wrapped into special
config nodes that make handling the config file much easier:

    - `jsoncfg.load()` and `jsoncfg.loads()` are very similar to the standard `json.loads()`.
      These functions allow you to load config files with extended syntax into bare python
      representation of the json data (dictionaries, lists, numbers, etc...).
    - `jsoncfg.load_config()` and `jsoncfg.loads_config()` load the json data into special wrapper
      objects that help you to query the config with much nicer syntax. At the same time if you
      are looking for a value that doesn't exist in the config then these problems are handled with
      exceptions that contain line/column number info about the location of the error.

One of the biggest problems with loading the config into bare python objects with a json library is
that the loaded json data doesn't contain the line/column numbers for the loaded json
nodes/elements. This means that by using a simple json library you can report the location of errors
with config file line/column numbers only in case of json syntax errors (in best case).
By loading the json nodes/elements into our wrapper objects we can retain the line/column numbers
for the json nodes/elements and we can use them in our error messages in case of semantic errors.

I assume that you have already installed json-cfg and you have the previously shown server config
example in a `server.cfg` file in the current directory.

This is how to load and process the above server configuration with a simple json library:

.. code-block:: python

    import json

    with open('server.cfg') as f:
        config = json.load(f)
    for server in config['servers']:
        listen_on_interface(server['ip_address'], server.get('port', 8000))
    superuser_name = config['superuser_name']

The same with json-cfg:

.. code-block:: python

    import jsoncfg

    config = jsoncfg.load_config('server.cfg')
    for server in config.servers:
        listen_on_interface(server.ip_address(), server.port(8000))
    superuser_name = config.superuser_name()

Seemingly the difference isn't that big. With json-cfg you can use extended syntax in the config
file and the code that loads/processes the config is also somewhat nicer but real difference is
what happens when we encounter an error. With json-cfg you get an exception with a message that
points to the problematic part of the json config file while the pure-json example can't tell you
line/column numbers in the config file. In case of larger configs this can cause headaches.

Open your `server.cfg` file and remove the required `ip_address` attribute from one of the server
config blocks. This will cause an error when we try to load the config file with the above code
examples. The above code snippets report the following error messages in this scenario:

json:

.. code-block::

    KeyError: 'ip_address'

json-cfg:

.. code-block::

    jsoncfg.config_classes.JSONConfigValueNotFoundError: Required config node not found. Missing query path: .ip_address (relative to error location) [line=3;col=9]

Detailed explanation of the library interface
---------------------------------------------

When you load your json with `jsoncfg.load_config()` or `jsoncfg.loads_config()` the returned json
data - the hierarchy - is a tree of wrapper objects provided by this library. These wrapper objects
make it possible to store the column/line numbers for each json node/element (for error reporting)
and these wrappers allow you to query the config with the nice syntax you've seen above.

This library differentiates 3 types of json nodes/elements and each of these have their own wrapper
classes:

- json object (dictionary like stuff)
- json array (list like stuff)
- json scalar (I use "scalar" to refer any json value that isn't a container - object or array)

I use *json value* to refer to a json node/element whose type is unknown or unimportant.
The public API of the wrapper classes is very simple: they have no public methods. All they provide
is a few magic methods that you can use to read/query the loaded json data. (These magic methods
are `__contains__`, `__getattr__`, `__getitem__`, `__len__`, `__iter__` and `__call__` but don't
worry if you don't about these magic methods as I will demonstrate the usage with simple code
examples that don't assume that you know these magic methods.)
The reason for having no public methods is simple: We allow querying json object keys with
`__getattr__` (with the dot or member access operator like `config.myvalue`) and we don't want any
public methods to conflict with the key values in your config file.

After loading the config you have a tree of wrapper object nodes and you have to perform these two
operations to get values from the config:

1. querying/reading/traversing the json hierarchy: the result of querying is a wrapper object
2. fetching the python value from the selected wrapper object: this can be done by calling the
   queried wrapper object.

The following sections explain these two operations in more detail.

Querying the json config hierarchy
""""""""""""""""""""""""""""""""""

To read and query the json hierarchy and the wrapper object nodes that build up the tree you have
to exploit the `__contains__`, `__getattr__`, `__getitem__`, `__len__`, `__iter__` magic methods
of the wrapper objects. We will use the previously shown server config for the following examples.

.. code-block:: python

    import jsoncfg

    config = jsoncfg.load_config('server.cfg')

    # Using __getattr__ to get the servers key from the config json object.
    # The result of this expression is a wrapper object that wraps the servers array/list.
    server_array = config.servers

    # The equivalent of the previous expression using __getitem__:
    server_array = config['servers']

    # Note that querying a non-existing key from an object doesn't raise an error. Instead
    # it returns a special ValueNotFoundNode instance that you can continue using as a
    # wrapper object. The error happens only if you try to fetch the value of this key
    # without specifying a default value - but more on this later in the section where we
    # discuss value fetching from wrapper objects.
    special_value_not_found_node = config.non_existing_key

    # Checking whether a key exists in a json object:
    servers_exists = 'servers' in config

    # Using __getitem__ to index into json array wrapper objects:
    # Over-indexing the array would raise an exception with useful error message
    # containing the location of the servers_array in the config file.
    first_item_wrapper_object = servers_array[0]

    # Getting the length of json object and json array wrappers:
    num_config_key_value_pairs = len(config)
    servers_array_len = len(servers_array)

    # Iterating the items of a json object or array:
    for key_string, value_wrapper_object in config:
        pass
    for value_wrapper_object in config.servers:
        pass

Not all node types (object, array, scalar) support all operations. For example a scalar json value
doesn't support `len()` and you can not iterate it. What happens if someone puts a scalar value
into the config in place of the servers array? In that case the config loader code will sooner or
later performs an array-specific operation on that scalar value (for example iteration) that will
raise an exception with a useful error message pointing the the loader code with the stack trace and
pointing to the scalar value in the config file with line/column numbers. You will find more
json-node-type related checks and error handling mechanisms in the following sections (value
fetching and error handling).

Fetching python values from the queried wrapper objects
"""""""""""""""""""""""""""""""""""""""""""""""""""""""

After selecting any of the wrapper object nodes from the json config hierarchy you can fetch its
wrapped value by using its `__call__` magic method. This works on all json node types: objects,
arrays and scalars. If you fetch a container (object or array) then it will fetch the raw unwrapped
values recursively - it fetches the whole subtree whose root node is the fetched wrapper object.

.. code-block:: python

    import jsoncfg

    config = jsoncfg.load_config('server.cfg')

    # Fetching the value of the whole json object hierarchy.
    # python_hierarchy now looks like something you normally
    # get as a result of a standard `json.load()`.
    python_hierarchy = config()

    # Converting only the servers array into python-object format:
    python_server_list = config.servers()

    # Getting the ip_address of the first server.
    server_0_ip_address_str = config.servers[0].ip_address()


Fetching optional config values (by specifying a default value)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The value fetcher call has some optional parameters. You can call it with an optional default value
followed by zero or more `jsoncfg.JSONValueMapper` instances. The default value comes in handy when
you are querying an **optional** item from a json object:

.. code-block:: python

    # If "optional_value" isn't in the config then return the default value (50).
    v0 = config.optional_value(50)
    # This raises an exception if "required_value" isn't in the config.
    v1 = config.required_value()


Using value mappers to validate and/or transform fetched values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Whether you are using a default value or not you can specify zero or more `jsoncfg.JSONValueMapper`
instances too in the parameter list of the fetcher function call. These instances have to be
callable, they have to have a `__call__` method that receives one parameter - the fetched value -
and they have to return the transformed (or untouched) value. If you specify more than value value
mapper instances then these value mappers are applied to the fetched value in left-to-right order
as you specify them in the argument list. You can use these value mapper instances not only to
transform the fetched value, but also to perform (type) checks on them. The `jsoncfg.value_mappers`
module contains a few predefined type-checkers but you can create your own value mappers.

.. warning::

    If you specify both a default value and one or more value mapper instances in your value fetcher
    call then the value mappers are never applied to the default value. The value mappers are used
    only when you fetch a value that exists in the config. json-cfg uses either the default value
    or the list of value mapper instances but not both.

.. code-block:: python

    from jsoncfg.value_mappers import RequireType
    from jsoncfg.value_mappers import require_list, require_string, require_integer, require_number

    # require_list is a jsoncfg.JSONValueMapper instance that checks if the fetched value is a list.
    # If the "servers" key is missing form the config or its type isn't list then an exception is
    # raised because we haven't specified a default value.
    python_server_list = config.servers(require_list)

    # If the "servers" key is missing from the config then the return value is None. If "servers"
    # is in the config and it isn't a list instance then an exception is raised otherwise the
    # return value is the servers list.
    python_server_list = config.servers(None, require_list)

    # Querying the required ip_address parameter with required string type.
    ip_address = config.servers[0].ip_address(require_string)

    # Querying the optional port parameter with a default value of 8000.
    # If the optional port parameter is specified in the config then it has to be an integer.
    ip_address = config.servers[0].port(8000, require_integer)

    # An optional timeout parameter with a default value of 5. If the timeout parameter is in
    # the config then it has to be a number (int, long, or float).
    timeout = config.timeout(5, require_number)

    # Getting a required guest_name parameter from the config. The parameter has to be either
    # None (null in the json file) or a string.
    guest_name = config.guest_name(RequireType(type(None), str))


Writing a custom value mapper (or validator)
````````````````````````````````````````````

- Derive your own value mapper class from `jsoncfg.JSONValueMapper`.
- Implement the `__call__` method that receives one value and returns one value:

    - Your `__call__` method can return the received value intact but it is allowed to
      return a completely different transformed value.
    - Your `__call__` implementation can perform validation. If the validation fails then
      you have to raise an exception. This exception can be anything but if you don't have
      a better idea then simply use the standard `ValueError` or `TypeError`. This exception
      will be caught by the value fetcher call and it re-raises another json-cfg specific
      exception that contains useful error message with the location of the error and that
      exception also contains the exception you raised while validating.

Custom value mapper example code:

.. code-block:: python

    import datetime
    import jsoncfg
    from jsoncfg import JSONValueMapper
    from jsoncfg.value_mappers import require_integer

    class OneOf(JSONValueMapper):
        def __init__(self, *enum_members):
            self.enum_members = set(enum_members)

        def __call__(self, v):
            if v not in self.enum_members:
                raise ValueError('%r is not on of these: %r' % (v, self.enum_members))
            return v

    class RangeCheck(JSONValueMapper):
        def __init__(self, min_, max_):
            self.min = min_
            self.max = max_

        def __call__(self, v):
            if self.min <= v < self.max:
                return v
            raise ValueError('%r is not in range [%r, %r)' % (v, self.min, self.max))

    class ToDateTime(JSONValueMapper):
        def __call__(self, v):
            if not isinstance(v, str):
                raise TypeError('Expected a naive iso8601 datetime string but found %r' % v)
            return datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S')
    to_datetime = ToDateTime()

    config = jsoncfg.load_config('server.cfg')

    # Creating an instance for reuse.
    require_cool_superuser_name = OneOf('tron', 'neo')
    superuser_name = config.superuser_name(None, require_cool_superuser_name)

    check_http_port_range = RangeCheck(8000, 9000)
    port = config.servers[0].port(8000, check_http_port_range)

    # Chaining value mappers:
    port = config.servers[0].port(8000, require_integer, check_http_port_range)

    # to_datetime converts a naive iso8601 datetime string into a datetime instance.
    superuser_birthday = config.superuser_birthday(None, to_datetime)


Error handling: exceptions
--------------------------

The base of all library exceptions is `jsoncfg.JSONConfigException`. If the parsed json contains a
syntax error then you receive a `jsoncfg.JSONConfigParserException` - this exception has no
subclasses. In case of config query errors you receive a `jsoncfg.JSONConfigQueryError` - this
exception has several subclasses.

.. code-block::

                         +---------------------+
                         | JSONConfigException |
                         +---------------------+
                            ▲               ▲
                            |               |
        +-------------------+-------+       |
        | JSONConfigParserException |       |
        +---------------------------+       |
                                      +-----+----------------+
              +---------------------->+ JSONConfigQueryError +<------------------------+
              |                       +----------------------+                         |
              |                          ▲                ▲                            |
              |                          |                |                            |
              |   +----------------------------+    +------------------------------+   |
              |   | JSONConfigValueMapperError |    | JSONConfigValueNotFoundError |   |
              |   +----------------------------+    +------------------------------+   |
              |                                                                        |
        +-----+-------------------+                                   +----------------+-----+
        | JSONConfigNodeTypeError |                                   | JSONConfigIndexError |
        +-------------------------+                                   +----------------------+

`jsoncfg.JSONConfigException`

    This is the mother of all exceptions raised by the library (aside from some some `ValueError`s
    and `TypeErrors` that are raised in case of trivial programming mistakes). Note that this
    exception is never raised directly - the library raises only exceptions that are derived from
    this.

`jsoncfg.JSONConfigParserException`

    You receive this exception if there is a syntax error in the parsed json.

    - `error_message`: The error message without the line/column number
      info. The standard `Exception.message` field contains this very same message but with the
      line/column info formatted into it as a postfix.
    - `line`, `column`: line and column information to locate the error easily in the parsed json.

`jsoncfg.JSONConfigQueryError`

    You receive this exception in case of errors you make while processing the parsed json. This
    exception class is never instantiated directly, only its subclasses are used.

    - `config_node`: The json node/element that was processed when the error happened.
    - `line`, `column`: line and column information to locate the error easily in the parsed json.

`jsoncfg.JSONConfigValueMapperError`

    Raised when you query and fetch a value by specifying a value mapper but the value mapper
    instance raises an exception during while fetching the value.

    - `mapper_exception`: The exception instance raised by the value mapper.

`jsoncfg.JSONConfigValueNotFoundError`

    This is raised when you try to fetch a required (non-optional) value that doesn't exist in the
    config file.

`jsoncfg.JSONConfigNodeTypeError`

    You get this exception if you try to perform an operation on a node that is not allowed for
    that node type (object, array or scalar), for example indexing into an array with a string.

`jsoncfg.JSONConfigIndexError`

    Over-indexing a json array results in this exception.

    - `index`: The index used to over-index the array.

Utility functions
-----------------

TODO: Coming soon... The config wrapper objects have no public methods but in some cases you may
want to extract some info from them (for example line/column number, type of node). You can
do that with utility functions that can be imported from the `jsoncfg` module.
