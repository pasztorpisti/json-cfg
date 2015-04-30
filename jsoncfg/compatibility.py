"""
This file concentrates the weird stuff that helps this lib to work with
both python 2 and 3. Fortunately this stuff isn't that much so I don't
want to depend on larger compatibility libraries.
"""

import sys

python2 = sys.version_info[0] == 2


xrange = xrange if python2 else range
unichr = unichr if python2 else chr

if python2:
    def is_unicode(s):
        return isinstance(s, unicode)

    def utf8chr(codepoint):
        return unichr(codepoint).encode('utf-8')

    unicode = unicode
else:
    def is_unicode(s):
        return isinstance(s, str)

    # This is here just to satisfy import statements.
    def utf8chr(codepoint):
        return RuntimeError('This should never be called in case of python3.')

    unicode = str
