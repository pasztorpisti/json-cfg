from unittest import TestCase

from jsoncfg.compatibility import python2
from jsoncfg.utils import detect_encoding_and_remove_bom, decode_utf_text_buffer


class TestEncodingFunctions(TestCase):
    def test_detect_encoding_and_remove_bom(self):
        encoded_decoded_pairs = (
            (b'\xef\xbb\xbfUTF', u'UTF'),
            (b'\xff\xfe\0\0U\0\0\0T\0\0\0F\0\0\0', u'UTF'),
            (b'\0\0\xfe\xff\0\0\0U\0\0\0T\0\0\0F', u'UTF'),
            (b'\xff\xfeU\0T\0F\0', u'UTF'),
            (b'\xfe\xff\0U\0T\0F', u'UTF'),
            (b'UTF', u'UTF'),
        )
        for encoded, decoded in encoded_decoded_pairs:
            buf, encoding = detect_encoding_and_remove_bom(encoded)
            self.assertEqual(buf.decode(encoding), decoded)

    def test_decode_text_buffer(self):
        self.assertEqual(decode_utf_text_buffer(b'\xef\xbb\xbfUTF', use_utf8_strings=False), u'UTF')
        if python2:
            # Testing use_utf8_strings=True/False with buf=utf8/utf16. -> 4 cases.
            self.assertEqual(decode_utf_text_buffer(b'\xef\xbb\xbfUTF', use_utf8_strings=False),
                             u'UTF')
            self.assertEqual(decode_utf_text_buffer(b'\xef\xbb\xbfUTF', use_utf8_strings=True),
                             b'UTF')
            self.assertEqual(decode_utf_text_buffer(b'\xff\xfe\0\0U\0\0\0T\0\0\0F\0\0\0',
                                                    use_utf8_strings=False), u'UTF')
            self.assertEqual(decode_utf_text_buffer(b'\xff\xfe\0\0U\0\0\0T\0\0\0F\0\0\0',
                                                    use_utf8_strings=True), b'UTF')
