# coding: utf-8

import re
from django.utils.six.moves import html_parser
HTMLParser = html_parser.HTMLParser
HTMLParseError = html_parser.HTMLParseError
from postmarkup import render_bbcode
from json import JSONEncoder
try:
    import markdown
except ImportError:
    pass

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.utils.functional import Promise
from django.utils.translation import check_for_language
from django.utils.encoding import force_text
from django.template.defaultfilters import urlize as django_urlize
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.contrib.sites.models import Site

from djangobb_forum import settings as forum_settings


#compile smiles regexp
_SMILES = [(re.compile(smile_re), path) for smile_re, path in forum_settings.SMILES]


def absolute_url(path):
    return 'http://%s%s' % (Site.objects.get_current().domain, path)


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


class HTMLFilter(HTMLParser):
        """
        Base class for html parsers that produce filtered output.
        """

        def __init__(self):
            HTMLParser.__init__(self)
            self.html = []

        def handle_starttag(self, tag, attrs):
            self.html.append('<%s%s>' % (tag, self.__html_attrs(attrs)))

        def handle_data(self, data):
            self.html.append(data)

        def handle_startendtag(self, tag, attrs):
            self.html.append('<%s%s/>' % (tag, self.__html_attrs(attrs)))

        def handle_endtag(self, tag):
            self.html.append('</%s>' % tag)

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


class ExcludeTagsHTMLFilter(HTMLFilter):
        """
        Class for html parsing with excluding specified tags.
        """

        def __init__(self, func, tags=('a', 'pre', 'span')):
            HTMLFilter.__init__(self)
            self.func = func
            self.is_ignored = False
            self.tags = tags

        def handle_starttag(self, tag, attrs):
            if tag in self.tags:
                self.is_ignored = True
            HTMLFilter.handle_starttag(self, tag, attrs)

        def handle_data(self, data):
            if not self.is_ignored:
                data = self.func(data)
            HTMLFilter.handle_data(self, data)

        def handle_endtag(self, tag):
            self.is_ignored = False
            HTMLFilter.handle_endtag(self, tag)


def urlize(html):
    """
    Urlize plain text links in the HTML contents.

    Do not urlize content of A and CODE tags.
    """
    try:
        parser = ExcludeTagsHTMLFilter(django_urlize)
        parser.feed(html)
        urlized_html = parser.html
        parser.close()
    except HTMLParseError:
        # HTMLParser from Python <2.7.3 is not robust
        # see: http://support.djangobb.org/topic/349/
        if settings.DEBUG:
            raise
        return html
    return urlized_html

def _smile_replacer(data):
    for smile, path in _SMILES:
        data = smile.sub(path, data)
    return data

def smiles(html):
    """
    Replace text smiles.
    """
    try:
        parser = ExcludeTagsHTMLFilter(_smile_replacer)
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


class AddAttributesHTMLFilter(HTMLFilter):
    """
    Class for html parsing that adds given attributes to tags.
    """

    def __init__(self, add_attr_map):
        HTMLFilter.__init__(self)
        self.add_attr_map = dict(add_attr_map)

    def handle_starttag(self, tag, attrs):
        attrs = list(attrs)
        for add_attr in self.add_attr_map.get(tag, []):
            if add_attr not in attrs:
                attrs.append(add_attr)

        HTMLFilter.handle_starttag(self, tag, attrs)


def add_rel_nofollow(html):
    """
    Add rel="nofollow" to <a> tags so that search engines don't give them weight.

    Untrusted links should have rel="nofollow" to dissuade spammers from
    posting for SEO purposes.  For more information, see
    https://en.wikipedia.org/wiki/Nofollow.
    """
    try:
        parser = AddAttributesHTMLFilter({'a': [('rel', 'nofollow')]})
        parser.feed(html)
        output_html = parser.html
        parser.close()
    except HTMLParseError:
        # HTMLParser from Python <2.7.3 is not robust
        # see: http://support.djangobb.org/topic/349/
        if settings.DEBUG:
            raise
        return html
    return output_html


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


def convert_text_to_html(text, markup):
    if markup == 'bbcode':
        text = render_bbcode(text)
    elif markup == 'markdown':
        text = markdown.markdown(text, safe_mode='escape')
    else:
        raise Exception('Invalid markup property: %s' % markup)
    text = urlize(text)
    if forum_settings.NOFOLLOW_LINKS:
        text = add_rel_nofollow(text)
    return text

