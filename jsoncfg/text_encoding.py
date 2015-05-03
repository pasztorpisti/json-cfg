from .compatibility import python2, my_basestring


def load_utf_text_file(file_, default_encoding='UTF-8', use_utf8_strings=True):
    """
    Loads the specified text file and tries to decode it using one of the UTF encodings.
    :param file_: The path to the loadable text file or a file-like object with a read() method.
    :param default_encoding: The encoding to be used if the file doesn't have a BOM prefix.
    :param use_utf8_strings: Ignored in case of python3, in case of python2 the default
    value of this is True. True means that the loaded json string should be handled as a utf-8
    encoded str instead of a unicode object.
    :return: A unicode object. In case of python2 it can optionally be an str object
    containing utf-8 encoded text.
    """
    if isinstance(file_, my_basestring):
        with open(file_, 'rb') as f:
            buf = f.read()
    else:
        buf = file_.read()
    return decode_utf_text_buffer(buf, default_encoding, use_utf8_strings)


def decode_utf_text_buffer(buf, default_encoding='UTF-8', use_utf8_strings=True):
    """
    :param buf: Binary file contents with optional BOM prefix.
    :param default_encoding: The encoding to be used if the buffer
    doesn't have a BOM prefix.
    :param use_utf8_strings: Used only in case of python2: You can choose utf-8
    str in-memory string representation in case of python. If use_utf8_strings is
    False or you are using python3 then the text buffer is automatically loaded as a
    unicode object.
    :return: A unicode object. In case of python2 it can optionally be an str object
    containing utf-8 encoded text.
    """
    buf, encoding = detect_encoding_and_remove_bom(buf, default_encoding)
    if python2 and use_utf8_strings:
        if are_encoding_names_equivalent(encoding, 'UTF-8'):
            return buf
        return buf.decode(encoding).encode('UTF-8')
    return buf.decode(encoding)


def are_encoding_names_equivalent(encoding0, encoding1):
    encoding0 = encoding0.replace('-', '').lower()
    encoding1 = encoding1.replace('-', '').lower()
    return encoding0 == encoding1


def detect_encoding_and_remove_bom(buf, default_encoding='UTF-8'):
    """
    :param buf: Binary file contents with an optional BOM prefix.
    :param default_encoding: The encoding to be used if the buffer
    doesn't have a BOM prefix.
    :return: (buf_without_bom_prefix, encoding)
    """
    assert isinstance(buf, bytes)
    for bom, encoding in _byte_order_marks:
        if buf.startswith(bom):
            return buf[len(bom):], encoding
    return buf, default_encoding


_byte_order_marks = (
    (b'\xef\xbb\xbf', 'UTF-8'),
    # It's important to check UTF-32-LE *before* UTF-16-LE.
    (b'\xff\xfe\x00\x00', 'UTF-32-LE'),
    (b'\x00\x00\xfe\xff', 'UTF-32-BE'),
    (b'\xff\xfe', 'UTF-16-LE'),
    (b'\xfe\xff', 'UTF-16-BE'),
)
