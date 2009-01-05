# -*- coding: utf-8 -*-
r"""
    phpserialize
    ~~~~~~~~~~~~

    a port of the ``serialize`` and ``unserialize`` functions of
    php to python.  This module implements the python serialization
    interface (eg: provides `dumps`, `loads` and similar functions).

    Usage
    =====

    >>> from phpserialize import *
    >>> obj = dumps("Hello World")
    >>> loads(obj)
    'Hello World'

    Due to the fact that PHP doesn't know the concept of lists, lists
    are serialized like hash-maps in PHP.  As a matter of fact the
    reverse value of a serialized list is a dict:

    >>> loads(dumps(range(2)))
    {0: 0, 1: 1}

    If you want to have a list again, you can use the `dict_to_list`
    helper function:

    >>> dict_to_list(loads(dumps(range(2))))
    [0, 1]

    It's also possible to convert into a tuple by using the `dict_to_tuple`
    function:

    >>> dict_to_tuple(loads(dumps((1, 2, 3))))
    (1, 2, 3)

    Another problem are unicode strings.  By default unicode strings are
    encoded to 'utf-8' but not decoded on `unserialize`.  The reason for
    this is that phpserialize can't guess if you have binary or text data
    in the strings:

    >>> loads(dumps(u'Hello W\xf6rld'))
    'Hello W\xc3\xb6rld'

    If you know that you have only text data of a known charset in the result
    you can decode strings by setting `decode_strings` to True when calling
    loads:

    >>> loads(dumps(u'Hello W\xf6rld'), decode_strings=True)
    u'Hello W\xf6rld'

    Dictionary keys are limited to strings and integers.  `None` is converted
    into an empty string and floats and booleans into integers for PHP
    compatibility:

    >>> loads(dumps({None: 14, 42.23: 'foo', True: [1, 2, 3]}))
    {'': 14, 1: {0: 1, 1: 2, 2: 3}, 42: 'foo'}

    It also provides functions to read from file-like objects:

    >>> from StringIO import StringIO
    >>> stream = StringIO('a:2:{i:0;i:1;i:1;i:2;}')
    >>> dict_to_list(load(stream))
    [1, 2]

    And to write to those:

    >>> stream = StringIO()
    >>> dump([1, 2], stream)
    >>> stream.getvalue()
    'a:2:{i:0;i:1;i:1;i:2;}'

    Like `pickle` chaining of objects is supported:

    >>> stream = StringIO()
    >>> dump([1, 2], stream)
    >>> dump("foo", stream)
    >>> stream.seek(0)
    >>> load(stream)
    {0: 1, 1: 2}
    >>> load(stream)
    'foo'

    This feature however is not supported in PHP.  PHP will only unserialize
    the first object.

    CHANGELOG
    =========

    1.1
        -   added `dict_to_list` and `dict_to_tuple`
        -   added support for unicode
        -   allowed chaining of objects like pickle does.


    :copyright: 2007-2008 by Armin Ronacher.
    license: BSD
"""
from StringIO import StringIO

__author__ = 'Armin Ronacher <armin.ronacher@active-4.com>'
__version__ = '1.1'


def dumps(data, charset='utf-8', errors='strict'):
    """Return the PHP-serialized representation of the object as a string,
    instead of writing it to a file like `dump` does.
    """
    def _serialize(obj, keypos):
        if keypos:
            if isinstance(obj, (int, long, float, bool)):
                return 'i:%i;' % obj
            if isinstance(obj, basestring):
                if isinstance(obj, unicode):
                    obj = obj.encode(charset, errors)
                return 's:%i:"%s";' % (len(obj), obj)
            if obj is None:
                return 's:0:"";'
            raise TypeError('can\'t serialize %r as key' % type(obj))
        else:
            if obj is None:
                return 'N;'
            if isinstance(obj, bool):
                return 'b:%i;' % obj
            if isinstance(obj, (int, long)):
                return 'i:%s;' % obj
            if isinstance(obj, float):
                return 'd:%s;' % obj
            if isinstance(obj, basestring):
                if isinstance(obj, unicode):
                    obj = obj.encode(charset, errors)
                return 's:%i:"%s";' % (len(obj), obj)
            if isinstance(obj, (list, tuple, dict)):
                out = []
                if isinstance(obj, dict):
                    iterable = obj.iteritems()
                else:
                    iterable = enumerate(obj)
                for key, value in iterable:
                    out.append(_serialize(key, True))
                    out.append(_serialize(value, False))
                return 'a:%i:{%s}' % (len(obj), ''.join(out))
            raise TypeError('can\'t serialize %r' % type(obj))
    return _serialize(data, False)


def load(fp, charset='utf-8', errors='strict', decode_strings=False):
    """Read a string from the open file object `fp` and interpret it as a
    data stream of PHP-serialized objects, reconstructing and returning
    the original object hierarchy.

    `fp` must provide a `read()` method that takes an integer argument.  Both
    method should return strings.  Thus `fp` can be a file object opened for
    reading, a `StringIO` object, or any other custom object that meets this
    interface.

    `load` will read exactly one object from the stream.  See the docstring of
    the module for this chained behavior.
    """
    def _expect(e):
        v = fp.read(len(e))
        if v != e:
            raise ValueError('failed expectation, expected %r got %r' % (e, v))

    def _read_until(delim):
        buf = []
        while 1:
            char = fp.read(1)
            if char == delim:
                break
            elif not char:
                raise ValueError('unexpected end of stream')
            buf.append(char)
        return ''.join(buf)

    def _unserialize():
        type_ = fp.read(1).lower()
        if type_ == 'n':
            _expect(';')
            return None
        if type_ in 'idb':
            _expect(':')
            data = _read_until(';')
            if type_ == 'i':
                return int(data)
            if type_ == 'd':
                return float(data)
            return int(data) != 0
        if type_ == 's':
            _expect(':')
            length = int(_read_until(':'))
            _expect('"')
            data = fp.read(length)
            _expect('"')
            if decode_strings:
                data = data.decode(charset, errors)
            _expect(';')
            return data
        if type_ == 'a':
            _expect(':')
            items = int(_read_until(':')) * 2
            _expect('{')
            result = {}
            last_item = Ellipsis
            for idx in xrange(items):
                item = _unserialize()
                if last_item is Ellipsis:
                    last_item = item
                else:
                    result[last_item] = item
                    last_item = Ellipsis
            _expect('}')
            return result
        raise ValueError('unexpected opcode')

    return _unserialize()


def loads(data, charset='utf-8', errors='strict', decode_strings=False):
    """Read a PHP-serialized object hierarchy from a string.  Characters in the
    string past the object's representation are ignored.
    """
    return load(StringIO(data), charset, errors, decode_strings)


def dump(data, fp, charset='utf-8', errors='strict'):
    """Write a PHP-serialized representation of obj to the open file object
    `fp`.  Unicode strings are encoded to `charset` with the error handling
    of `errors`.

    `fp` must have a `write()` method that accepts a single string argument.
    It can thus be a file object opened for writing, a `StringIO` object, or
    any other custom object that meets this interface.
    """
    fp.write(dumps(data, charset, errors))


def dict_to_list(d):
    """Converts an ordered dict into a list."""
    try:
        return [d[x] for x in xrange(len(d))]
    except KeyError:
        raise ValueError('dict is not a sequence')


def dict_to_tuple(d):
    """Converts an ordered dict into a tuple."""
    return tuple(dict_to_list(d))


serialize = dumps
unserialize = loads


if __name__ == '__main__':
    import doctest
    doctest.testmod()
