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


The goal of this library is providing a json config file loader that has
the following extras compared to the standard `json.load()`:

- A larger subset of javascript (and not some weird/exotic extension to json that
  would turn json into something that has nothing to do with json/javascript):

    - backward compatible with json so you can still load standard json files too
    - single and multi-line comments - this is more useful then you would think:
      it is good not only for documentation but also for temporarily disabling
      a block in your config without actually deleting entries
    - object (dictionary) keys without quotes
    - trailing commas (allowing commas after the last item of objects and arrays)

- Providing line number information for each element of the loaded config file
  and using this to display useful error messages that help locating errors not
  only while parsing the file but also when processing/interpreting it.
- A nice config query syntax that handles default values, required elements and
  automatically raises an exception in case of error (with useful info including
  the location of the error in the config file).


Config file examples
--------------------

**A traditional json config file:**

.. code:: javascript

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
        "superusername": "tron"
    }

**Something similar with json-cfg:**

.. code:: javascript
    
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
        superusername: "tron",  // <-- optional trailing comma
    }

*Hint: use javascript syntax highlight in your text editor for json config files
whenever possible - this makes reading config files much easier especially when you
have a lot of comments or large commented config blocks.*

Installation
------------

.. code:: sh

    pip install json-cfg

Alternatively you can download the zipped library from https://pypi.python.org/pypi/json-cfg

Usage
-----

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
that you can detect the location of config problems only while the config file is being parsed so
you can detect only json syntax errors. By loading the json into special objects we can retain the
location of json nodes/elements and use them in our error messages if we find a semantic error
when we are processing the config data.

I assume that you have already installed json-cfg and you have the previously shown server config
example in a `server.cfg` file in the current directory.

This is how to load and use the above server configuration with json-cfg:

.. code:: python

    import jsoncfg

    config = jsoncfg.load_config('server.cfg')
    for server in config.servers:
        listen_on_interface(server.ip_address(), server.port(8000))
    user_name = config.superusername()

The same with a simple json library:

.. code:: python

    import json

    with open('server.cfg') as f:
        config = json.load(f)
    for server in config['servers']:
        listen_on_interface(server['ip_address'], server.get('port', 8000))
    user_name = config['superusername']

Seemingly the difference isn't that big. With json-cfg you can use extended syntax in the config
file and the code that loads the config is also somewhat nicer but real difference is what happens
when we encounter an error. With json-cfg you get an exception with a message that points to the
problematic part of the json config file while the pure-json example can't tell you the
location within the config file. In case of a larger configs this can cause headaches.

Open your `server.cfg` file and remove the required `ip_address` attribute from one of the server
config blocks. This will cause an error when we try to load the config file with the above code
examples. The above code snippets report the following error messages in this scenario:

json-cfg:

.. code::

    jsoncfg.config_classes.JSONConfigValueNotFoundError: Required config node not found. Missing query path: .ip_address (relative to error location) [line=3;col=9]

json:

.. code::

    KeyError: 'ip_address'

