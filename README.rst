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

.. image:: https://img.shields.io/pypi/v/json-cfg.svg?style=flat
    :target: https://pypi.python.org/pypi/json-cfg
    :alt: pypi

.. image:: https://img.shields.io/github/tag/pasztorpisti/json-cfg.svg?style=flat
    :target: https://github.com/pasztorpisti/json-cfg
    :alt: github

.. image:: https://img.shields.io/github/license/pasztorpisti/json-cfg.svg?style=flat
    :target: https://github.com/pasztorpisti/json-cfg/blob/master/LICENSE.txt
    :alt: license


The goal of this library is providing a json config file loader that has
the following extras compared to the standard json.loads():

- A larger subset of javascript (and not some weird/exotic extension to json that
  would turn json into something that has nothing to do with json/javascript):

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

*Hint: use javascript syntax highlight in your text editor for json config files
 whenever possible - this makes reading config files much easier especially when you
 have a lot of comments or large commented config blocks.*

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

Installation
------------

.. code:: sh

    pip install json-cfg

As an alternative you can download the zipped library from https://pypi.python.org/pypi/json-cfg

Brief code examples
-------------------

TODO

Detailed API docs
-----------------

TODO
