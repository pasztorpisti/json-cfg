"""
This file concentrates the weird stuff that helps this lib to work with
both python 2 and 3. Fortunately this stuff isn't that much so I don't
want to depend on larger compatibility libraries.
"""

import sys

python2 = sys.version_info[0] == 2


if python2:
    my_xrange = xrange
    my_unichr = unichr
    my_unicode = unicode
    my_basestring = basestring

    def utf8chr(code_point):
        return unichr(code_point).encode('utf-8')
else:
    my_xrange = range
    my_unichr = chr
    my_unicode = str
    my_basestring = str

    # This is here just to satisfy import statements.
    def utf8chr(_):
        raise RuntimeError('This should never be called in case of python3.')
