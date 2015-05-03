from unittest import TestCase
from jsoncfg.compatibility import python2, utf8chr


class TestFunctions(TestCase):
    def test_utf8chr(self):
        if python2:
            self.assertEquals(utf8chr(0x1234), u'\u1234'.encode('utf-8'))
        else:
            self.assertRaisesRegexp(
                RuntimeError,
                r'This should never be called in case of python3\.',
                utf8chr,
                0x1234
            )
