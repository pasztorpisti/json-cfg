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

    def utf8chr(codepoint):
        return chr(codepoint)

    unicode = str
