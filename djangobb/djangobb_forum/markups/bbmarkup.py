import re
from django.conf import settings
from django.utils.html import escape
from django.template.defaultfilters import linebreaksbr
from django.utils.safestring import mark_safe 


__all__ = ('BBCODE_RULES', 'bbcode')

BBCODE_RULES = [ (r'\[url\](.+?)\[/url\]', r'<a href="\1">\1</a>'),
        (r'\[url=(.+?)\](.+?)\[/url\]', r'<a href="\1">\2</a>'),
        (r'\[link\](.+?)\[/link\]', r'<a href="\1">\1</a>'),
        (r'\[link=(.+?)\](.+?)\[/link\]', r'<a href="\1">\2</a>'),
        (r'\[email\](.+?)\[/email\]', r'<a href="mailto:\1">\1</a>'),
        (r'\[email=(.+?)\](.+?)\[/email\]', r'<a href="mailto:\1">\2</a>'),
        (r'\[img\](.+?)\[/img\]', r'<img src="\1">'),
        (r'\[img=(.+?)\](.+?)\[/img\]', r'<img src="\1" alt="\2">'),
        (r'\[IMG\](.+?)\[/IMG\]', r'<img src="\1">'),
        (r'\[IMG=(.+?)\](.+?)\[/IMG\]', r'<img src="\1" alt="\2">'),
        (r'\[color=(.+?)\](.+?)\[/color\]', r'<span style="color:\1">\2</span>'),
        (r'\[b\](.+?)\[/b\]', r'<strong>\1</strong>'),
        (r'\[i\](.+?)\[/i\]', r'<em>\1</em>'),
        (r'\[u\](.+?)\[/u\]', r'<u>\1</u>'),
        (r'\[s\](.+?)\[/s\]', r'<strike>\1</strike>'),
        (r'\[quote\](.+?)\[/quote\]', r'<blockquote>\1</blockquote>'),
        (r'\[quote=(.+?)\](.+?)\[/quote\]', r'<blockquote><em>\1</em> <br /> \2</blockquote>'),
        (r'\[center\](.+?)\[/center\]', r'<div style="text-align: center;">\1</div>'),
        (r'\[big\](.+?)\[/big\]', r'<big>\1</big>'),
        (r'\[small\](.+?)\[/small\]', r'<small>\1</small>'),
        (r'\[list\](.+?)\[/list\]', r'<ul>\1</ul>'),
        (r'\[list\=(.+?)\](.+?)\[/list\]', r'<ol start="\1">\2</ol>'),
        (r'\[\*\]\s?(.*?)\n', r'<li>\1</li>'),
        (r'\[br\]', r'<br />') ]

BBCODE_RULES += getattr(settings, 'BBMARKUP_EXTRA_RULES', [])


BBCODE_RULES_COMPILED = []
for bbset in (getattr(settings, 'BBMARKUP_CUSTOM_RULES', []) or BBCODE_RULES):
    p = re.compile(bbset[0], re.DOTALL)
    BBCODE_RULES_COMPILED.append((p, bbset[1]))


def code_parser(matchobj):
    """
    Escaping bbcode and html tags between [code] tags.
    """

    value = matchobj.group(1)
    value = value.replace('[', '&#91;')
    value = value.replace(']', '&#93;')
    value = value.replace('<br />', '\n')
    return "<pre><code>%s</code></pre>" % value


def bbcode(value, linebr=True, code_parser=code_parser):
    """
    >>> data = '[code]print "Lorem [b]imsum[b]"[/code]'
    >>> bbcode(data)
    u'<pre><code>print &quot;Lorem &#91;b&#93;imsum&#91;b&#93;&quot;</code></pre>'
    >>> bbcode('[i]Lorem[/i] \\n [s]imsum[/s]')
    u'<em>Lorem</em> <br /> <strike>imsum</strike>'
    >>> bbmarkup.bbcode('[list] [*] 1\n [*]2\n [*] 3\n[/list]')
    u'<ul> <li>1</li> <li>2</li> <li>3</li></ul>'
    >>> bbmarkup.bbcode('[list=2] [*] a\n [*]b\n [*] c\n[/list]')
    u'<ol start="2"> <li>a</li> <li>b</li> <li>c</li></ol>'
    >>> bbmarkup.bbcode("[code]print 123\nprint '<br/>'[/code]")
    u'<pre><code>print 123\nprint &#39;&lt;br/&gt;&#39;</code></pre>'
    >>> bbmarkup.bbcode('[quote=test user]Test quote text[/quote]')
    u'<blockquote><em>test user</em> <br /> Test quote text</blockquote>'
    """

    value = escape(value)
    if linebr:
        value = linebreaksbr(value)
    value = re.sub(re.compile(r'\[code\](.+?)\[/code\]', re.DOTALL), code_parser, value)
    for bbset in BBCODE_RULES_COMPILED:
        value = bbset[0].sub(bbset[1], value)

    return mark_safe(value)
