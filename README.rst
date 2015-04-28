jsonconfig
==========

The goal of this project is to provide a json config file loader that provides
the following extras compared to the standard json.loads():

- A larger subset of javascript:

    - single and multi-line comments
    - object (dictionary) keys without quotes
    - trailing commas (allowing commas after the last item of objects and arrays)

- Providing line number information for each element of the loaded config file
  and using this to display useful error messages that help locating errors.
- A nice config query syntax that handles default values, required elements and
  automatically raises an exception in case of error (with useful info including
  the location of the error in the config file).

Config file examples
--------------------

*Hint: use javascript syntax highlight in your text editor for json config files whenever possible - this makes reading config files much easier especially when you have a lot of comments or large commented config blocks.*

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

**The same with jsonconfig:**

.. code:: javascript
    
    {
        // Note that we could get rid of most quotation marks.
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

Brief code examples
-------------------

TODO

Detailed API docs
-----------------

TODO
