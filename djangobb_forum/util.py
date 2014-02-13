# coding: utf-8

import re
from HTMLParser import HTMLParser, HTMLParseError
import postmarkup
from postmarkup.parser import strip_bbcode
from urlparse import urlparse
try:
    import markdown
except ImportError:
    pass

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.utils.functional import Promise
from django.utils.translation import force_unicode, check_for_language
from django.utils.simplejson import JSONEncoder
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.sites.models import Site

from djangobb_forum import settings as forum_settings

import logging
logger = logging.getLogger(__name__)


#compile smiles regexp
_SMILES = [(re.compile(smile_re), path) for smile_re, path in forum_settings.SMILES]

def absolute_url(path):
    return 'http://%s%s' % (Site.objects.get_current().domain, path)


def can_close_topic(user, topic):
    return user == topic.user and user.has_perm('djangobb_forum.delayed_close') and (timezone.now() - topic.created).total_seconds() >= forum_settings.TOPIC_CLOSE_DELAY


def paged(paged_list_name, per_page):
    """
    Parse page from GET data and pass it to view. Split the
    query set returned from view.
    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if not isinstance(result, dict) or 'paged_qs' not in result:
                return result
            try:
                page = int(request.GET.get('page', 1))
            except ValueError:
                page = 1

            real_per_page = per_page

            #if per_page_var:
                #try:
                    #value = int(request.GET[per_page_var])
                #except (ValueError, KeyError):
                    #pass
                #else:
                    #if value > 0:
                        #real_per_page = value

            from django.core.paginator import Paginator
            paginator = Paginator(result['paged_qs'], real_per_page)
            try:
                page_obj = paginator.page(page)
            except (InvalidPage, EmptyPage):
                raise Http404
            result[paged_list_name] = page_obj.object_list
            result['is_paginated'] = page_obj.has_other_pages(),
            result['page_obj'] = page_obj,
            result['page'] = page
            result['page_range'] = paginator.page_range,
            result['pages'] = paginator.num_pages
            result['results_per_page'] = paginator.per_page,
            result['request'] = request
            return result
        return wrapper

    return decorator


class LazyJSONEncoder(JSONEncoder):
    """
    This fing need to save django from crashing.
    """

    def default(self, o):
        if isinstance(o, Promise):
            return force_unicode(o)
        else:
            return super(LazyJSONEncoder, self).default(o)


class JsonResponse(HttpResponse):
    """
    HttpResponse subclass that serialize data into JSON format.
    """

    def __init__(self, data, mimetype='application/json'):
        json_data = LazyJSONEncoder().encode(data)
        super(JsonResponse, self).__init__(
            content=json_data, mimetype=mimetype)


def build_form(Form, _request, GET=False, *args, **kwargs):
    """
    Shorcut for building the form instance of given form class
    """

    if not GET and 'POST' == _request.method:
        form = Form(_request.POST, _request.FILES, *args, **kwargs)
    elif GET and 'GET' == _request.method:
        form = Form(_request.GET, _request.FILES, *args, **kwargs)
    else:
        form = Form(*args, **kwargs)
    return form


class ExcludeTagsHTMLParser(HTMLParser):
        """
        Class for html parsing with excluding specified tags.
        """

        def __init__(self, func, tags=('a', 'pre', 'span')):
            HTMLParser.__init__(self)
            self.func = func
            self.is_ignored = False
            self.tags = tags
            self.html = []

        def handle_starttag(self, tag, attrs):
            self.html.append('<%s%s>' % (tag, self.__html_attrs(attrs)))
            if tag in self.tags:
                self.is_ignored = True

        def handle_data(self, data):
            if not self.is_ignored:
                data = self.func(data)
            self.html.append(data)

        def handle_startendtag(self, tag, attrs):
            self.html.append('<%s%s/>' % (tag, self.__html_attrs(attrs)))

        def handle_endtag(self, tag):
            self.is_ignored = False
            self.html.append('</%s>' % (tag))

        def handle_entityref(self, name):
            self.html.append('&%s;' % name)

        def handle_charref(self, name):
            self.html.append('&#%s;' % name)

        def unescape(self, s):
            #we don't need unescape data (without this possible XSS-attack)
            return s

        def __html_attrs(self, attrs):
            _attrs = ''
            if attrs:
                _attrs = ' %s' % (' '.join([('%s="%s"' % (k, v)) for k, v in attrs]))
            return _attrs

        def feed(self, data):
            HTMLParser.feed(self, data)
            self.html = ''.join(self.html)


def filter_language(text):
    """
    Replaces filtered language in the given text with an asterisk.
    """
    return re.sub(forum_settings.LANGUAGE_FILTER, '*', text) if forum_settings.LANGUAGE_FILTER else text


def _smile_replacer(data):
    for smile, path in _SMILES:
        data = smile.sub(path, data)
    return data

def smiles(html):
    """
    Replace text smiles.
    """
    try:
        parser = ExcludeTagsHTMLParser(_smile_replacer)
        parser.feed(html)
        smiled_html = parser.html
        parser.close()
    except HTMLParseError:
        # HTMLParser from Python <2.7.3 is not robust
        # see: http://support.djangobb.org/topic/349/
        if settings.DEBUG:
            raise
        return html
    return smiled_html

def paginate(items, request, per_page, total_count=None):
    try:
        page_number = int(request.GET.get('page', 1))
    except ValueError:
        page_number = 1

    paginator = Paginator(items, per_page)
    pages = paginator.num_pages
    try:
        paged_list_name = paginator.page(page_number).object_list
    except (InvalidPage, EmptyPage):
        raise Http404
    return pages, paginator, paged_list_name

def set_language(request, language):
    """
    Change the language of session of authenticated user.
    """

    if check_for_language(language):
        request.session['django_language'] = language


def convert_text_to_html(text, profile):
    markup = profile.markup
    if markup == 'bbcode':
        renderbb = customize_postmarkup(profile.user.has_perm('djangobb_forum.post_external_links'))

        text =  renderbb(text)
    elif markup == 'markdown':
        text = markdown.markdown(text, safe_mode='escape')
    else:
        raise Exception('Invalid markup property: %s' % markup)
    return text

class WhitelistedImgTag(postmarkup.ImgTag):
    def render_open(self, parser, node_index):
        contents = self.get_contents(parser)
        self.skip_contents(parser)

        # Validate url to avoid any XSS attacks
        if self.params:
            url = self.params.strip()
        else:
            url = strip_bbcode(contents)

        url = url.replace(u'"', u"%22").strip()
        if not url:
            return u''
        try:
            scheme, netloc, path, params, query, fragment = urlparse(url)
            if not scheme:
                url = u'http://' + url
                scheme, netloc, path, params, query, fragment = urlparse(url)
        except ValueError:
            return u''
        if scheme.lower() not in (u'http', u'https', u'ftp'):
            return u''
        if not re.search(forum_settings.IMAGE_HOST_WHITELIST, netloc, re.IGNORECASE):
            raise UnapprovedImageError(url)

        return u'<img src="%s"></img>' % postmarkup.PostMarkup.standard_replace_no_break(url)

class UnapprovedImageError(Exception):
    def __init__(self, url):
        self.url = url
    def user_error(self):
        return _('Sorry, you need to host your images with a service like imageshack.com. Please update your image links or remove all BB code [img] tags. Bad image url: %s') % self.url
    def __str__(self):
        return repr(self.url)

class CSSClassTag(postmarkup.TagBase):
    def __init__(self, name, className, **kwargs):
        postmarkup.TagBase.__init__(self, name, inline=True)
        self.className = className

    def render_open(self, parser, node_index):
        return u'<span class="%s">' % self.className

    def render_close(self, parser, node_index):
        return u'</span>'

class RestrictedLinkTag(postmarkup.TagBase):
    _safe_chars = frozenset(u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-=/&?:%&#')

    _re_domain = re.compile(r"//([a-z0-9-\.]+\.)?scratch\.mit\.edu", re.UNICODE)

    allowed = False

    def __init__(self, name, **kwargs):
        super(RestrictedLinkTag, self).__init__(name, inline=True)

    def render_open(self, parser, node_index):

        tag_data = parser.tag_data
        nest_level = tag_data[u'link_nest_level'] = tag_data.setdefault(u'link_nest_level', 0) + 1

        if nest_level > 1:
            return u""

        if self.params:
            url = self.params.strip()
        else:
            url = self.get_contents_text(parser).strip()
            url = postmarkup.PostMarkup.standard_unreplace(url)

        if u':' not in url:
            url = u'http://' + url

        scheme, uri = url.split(u':', 1)

        if scheme not in [u'http', u'https'] or self._re_domain.match(uri.lower()) is None:
            return u'<span>' # Prevent smilies from the ":/" in "http://"

        def percent_encode(s):
            safe_chars = self._safe_chars
            def replace(c):
                if c not in safe_chars:
                    return u"%%%02X" % ord(c)
                else:
                    return c
            return u"".join([replace(c) for c in s])

        self.allowed = True
        return u'<a href="%s">' % postmarkup.PostMarkup.standard_replace_no_break(percent_encode(url))


    def render_close(self, parser, node_index):

        tag_data = parser.tag_data
        tag_data[u'link_nest_level'] -= 1

        if tag_data[u'link_nest_level'] > 0:
            return u''

        if self.allowed:
            return u'</a>'
        else:
            return u'</span>'

class FilteredLinkTag(postmarkup.TagBase):
    _safe_chars = frozenset(u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-=/&?:%&#')
    _re_youtube = re.compile(r'//(?:www\.)?youtube\.com/(?:watch\?(?:.*&)?v=|v/)([\w-]+)', re.UNICODE)
    allowed = False

    def __init__(self, name, **kwargs):
        super(FilteredLinkTag, self).__init__(name, inline=True)

    def render_open(self, parser, node_index):

        tag_data = parser.tag_data
        nest_level = tag_data[u'link_nest_level'] = tag_data.setdefault(u'link_nest_level', 0) + 1

        if nest_level > 1:
            return u""

        if self.params:
            url = self.params.strip()
        else:
            url = self.get_contents_text(parser).strip()
            url = postmarkup.PostMarkup.standard_unreplace(url)

        if u':' not in url:
            url = u'http://' + url

        scheme, uri = url.split(u':', 1)

        if scheme not in [u'http', u'https', u'data']:
            return u'<span>'

        def percent_encode(s):
            safe_chars = self._safe_chars
            def replace(c):
                if c not in safe_chars:
                    return u"%%%02X" % ord(c)
                else:
                    return c
            return u"".join([replace(c) for c in s])

        self.allowed = True
        if scheme != 'data':
            match = self._re_youtube.match(uri)
            if match is not None:
                return '<a href="%s">' % reverse('djangobb:show_youtube_video', args=(match.group(1),))

        return u'<a href="%s">' % postmarkup.PostMarkup.standard_replace_no_break(percent_encode(url))


    def render_close(self, parser, node_index):

        tag_data = parser.tag_data
        tag_data[u'link_nest_level'] -= 1

        if tag_data[u'link_nest_level'] > 0:
            return u''

        if self.allowed:
            return u'</a>'
        else:
            return u'</span>'

class QuoteTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super(QuoteTag, self).__init__(name, strip_first_newline=True)

    def render_open(self, parser, node_index):
        if self.params:
            return u'<blockquote><p class="bb-quote-author">%s wrote:</p>' % (postmarkup.PostMarkup.standard_replace(self.params))
        else:
            return u'<blockquote>'

    def render_close(self, parser, node_index):
        return u'</blockquote>'

class ScratchblocksTag(postmarkup.TagBase):

    def __init__(self, name, **kwargs):
        super(ScratchblocksTag, self).__init__(name, enclosed=True, strip_first_newline=True)

    def render_open(self, parser, node_index):
        contents = self.get_contents(parser).strip(u'\n')
        self.skip_contents(parser)
        return u'<pre class=blocks>%s</pre>' % postmarkup.PostMarkup.standard_replace(contents)


class AkismetSpamError(Exception):
    def user_error(self):
        return _('Sorry, your post looks like spam!')

def filter_akismet(text):
    is_spam = False
    try:
        from akismet import Akismet
        api = Akismet(
            key=forum_settings.AKISMET_API_KEY,
            blog_url=forum_settings.AKISMET_BLOG_URL,
            agent=forum_settings.AKISMET_AGENT,
            api_timeout=forum_settings.AKISMET_TIMEOUT)
        if api.verify_key():
            is_spam = api.comment_check(text)
        else:
            logger.error("Invalid Aksimet API key.", extra={'key': api.key, 'blog': api.blog_url, 'user_agent': api.user_agent})
    except Exception as e:
        logger.error("Error while checking Akismet", extra={'exception': e})
    if is_spam:
        raise AkismetSpamError()
    return text


# This allows us to control the bb tags
def customize_postmarkup(allow_external_links):
    custom_postmarkup = postmarkup.PostMarkup()
    add_tag = custom_postmarkup.tag_factory.add_tag
    custom_postmarkup.tag_factory.set_default_tag(postmarkup.DefaultTag)

    add_tag(CSSClassTag, 'b', 'bb-bold')
    add_tag(CSSClassTag, 'i', 'bb-italic')
    add_tag(CSSClassTag, 'u', 'bb-underline')
    add_tag(CSSClassTag, 's', 'bb-strikethrough')

    add_tag(ScratchblocksTag, 'scratchblocks')

    add_tag(FilteredLinkTag if allow_external_links else RestrictedLinkTag, 'url')

    add_tag(QuoteTag, 'quote')

    add_tag(postmarkup.SearchTag, u'wp',
            u"http://en.wikipedia.org/wiki/Special:Search?search=%s", u'wikipedia.com', None)
    add_tag(postmarkup.SearchTag, u'wiki',
            u"http://wiki.scratch.mit.edu/wiki/Special:Search?search=%s", u'wiki.scratch.mit.edu', None)
    add_tag(postmarkup.SearchTag, u'google',
            u"http://www.google.com/search?hl=en&q=%s&btnG=Google+Search", u'google.com', None)
    add_tag(postmarkup.SearchTag, u'dictionary',
            u"http://dictionary.reference.com/browse/%s", u'dictionary.com', None)
    add_tag(postmarkup.SearchTag, u'dict',
            u"http://dictionary.reference.com/browse/%s", u'dictionary.com', None)

    add_tag(WhitelistedImgTag, u'img')
    add_tag(postmarkup.ListTag, u'list')
    add_tag(postmarkup.ListItemTag, u'*')

    # removed 'size' and replaced it with 'big' and 'small'
    add_tag(CSSClassTag, u'big', u'bb-big')
    add_tag(CSSClassTag, u'small', u'bb-small')
    add_tag(postmarkup.ColorTag, u"color")
    add_tag(postmarkup.CenterTag, u"center")
    add_tag(postmarkup.PygmentsCodeTag, u'code', None)

    add_tag(postmarkup.SimpleTag, u"p", 'p')

    return custom_postmarkup
