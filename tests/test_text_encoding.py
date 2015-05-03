from unittest import TestCase
from mock import patch, MagicMock

from jsoncfg.compatibility import python2
from jsoncfg.text_encoding import detect_encoding_and_remove_bom, decode_utf_text_buffer,\
    load_utf_text_file


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

    def test_detect_encoding_and_remove_bom_with_non_bytes_buf(self):
        self.assertRaisesRegexp(TypeError, r'buf should be a bytes instance but it is a',
                                detect_encoding_and_remove_bom, u'non_bytes_buf')

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

    def test_load_utf_text_file_filename(self):
        with patch('jsoncfg.text_encoding.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            mock_file.read.return_value = b'file_contents'

            text = load_utf_text_file('fake.txt', use_utf8_strings=False)

        self.assertEqual(text, u'file_contents')
        mock_open.assert_called_with('fake.txt', 'rb')
        mock_file.read.assert_called_with()

    def test_load_utf_text_file_fileobject(self):
        mock_file = MagicMock()
        mock_file.read.return_value = b'file_contents'

        text = load_utf_text_file(mock_file, use_utf8_strings=False)

        self.assertEqual(text, u'file_contents')
        mock_file.read.assert_called_with()
