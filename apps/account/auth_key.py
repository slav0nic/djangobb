import os
from datetime import datetime
import hashlib
import time
from base64 import b64encode, b64decode
from urllib import urlencode
from cgi import parse_qs

from django.conf import settings

def strftime(when):
    return when.strftime('%d-%m-%y-%H-%M-%S')


def strptime(when):
    try:
        return datetime.fromtimestamp(time.mktime(
            time.strptime(when, '%d-%m-%y-%H-%M-%S')))
    except ValueError:
        return None


def generate_key(**kwargs):
    """
    Return the hash of kwargs and the
    "one string" representation of hash and kwargs
    """

    pairs = []
    for key, value in kwargs.iteritems():
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        if isinstance(value, datetime):
            value = strftime(value)
        pairs.append((key, value))
    hash = hashlib.sha1(settings.SECRET_KEY + urlencode(pairs)).hexdigest()
    pairs.append(('_hash', hash))
    return hash, b64encode(urlencode(pairs))


def wrap_url(url, **kwargs):
    """
    Create new authorization key and append it to the url.
    """

    hash, b64 = generate_key(**kwargs)
    clue = '?' in url and '&' or '?'
    url = '%s%sauthkey=%s' % (url, clue, b64)
    return url


def decode_key(b64):
    return dict((x[0], x[1][0]) for x in parse_qs(b64decode(b64)).iteritems())


def validate_key(b64):
    if b64:
        kwargs = decode_key(b64)
        kwargs.pop('_hash')
        expired = strptime(kwargs.get('expired'))
        if expired:
            real_key, real_b64 = generate_key(**kwargs)
            if real_b64 == b64 and datetime.now() < expired:
                return True
    return False
