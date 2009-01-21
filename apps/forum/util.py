from datetime import datetime
import os.path
import random
import re
from HTMLParser import HTMLParser

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils.functional import Promise
from django.utils.translation import force_unicode
from django.utils.simplejson import JSONEncoder
from django import forms
from django.template.defaultfilters import urlize as django_urlize

from apps.forum import settings as forum_settings

#compile smiles regexp
_SMILES = [(re.compile(smile_re), path) for smile_re, path in forum_settings.SMILES]

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use

    Examples::

      @render_to('some/tmpl.html')
      def view(request):
          if smth:
              return {'context': 'dict'}
          else:
              return {'context': 'dict'}, 'other/tmpl.html'

     2006-2009 Alexander Solovyov, new BSD License
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer

def absolute_url(path):
    return 'http://%s%s' % (forum_settings.HOST, path)

def paged(paged_list_name, per_page):#, per_page_var='per_page'):
    """
    Parse page from GET data and pass it to view. Split the
    query set returned from view.
    """
    
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            result = func(request, *args, **kwargs)
            if not isinstance(result, dict):
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
            result[paged_list_name] = paginator.page(page).object_list
            result['page'] = page
            result['page_list'] = range(1, paginator.num_pages + 1)
            result['pages'] = paginator.num_pages
            result['per_page'] = real_per_page
            result['request'] = request
            return result
        return wrapper

    return decorator


def ajax(func):
    """
    Checks request.method is POST. Return error in JSON in other case.

    If view returned dict, returns JsonResponse with this dict as content.
    """
    def wrapper(request, *args, **kwargs):
        if request.method == 'POST':
            try:
                response = func(request, *args, **kwargs)
            except Exception, ex:
                response = {'error': traceback.format_exc()}
        else:
            response = {'error': {'type': 403, 'message': 'Accepts only POST request'}}
        if isinstance(response, dict):
            return JsonResponse(response)
        else:
            return response
    return wrapper


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
    Shorcut for building the form instance of given form class.
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

        def __init__(self, func, tags=('a', 'code')):
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
            self.html.append('&%s;' % name)

        def __html_attrs(self, attrs):
            _attrs = ''
            if attrs:
                _attrs = ' %s' % (' '.join([('%s="%s"' % (k,v)) for k,v in attrs]))
            return _attrs

        def feed(self, data):
            HTMLParser.feed(self, data)
            self.html = ''.join(self.html)

def urlize(data):
    """
    Urlize plain text links in the HTML contents.
   
    Do not urlize content of A and CODE tags.
    """

    parser = ExcludeTagsHTMLParser(django_urlize)
    parser.feed(data)
    urlized_html = parser.html
    parser.close()
    return urlized_html

def _smile_replacer(data):
    for smile, path in _SMILES:
        data = smile.sub(path, data)
    return data

def smiles(data):
    """
    Replace text smiles.
    """

    parser = ExcludeTagsHTMLParser(_smile_replacer)
    parser.feed(data)
    smiled_html = parser.html
    parser.close()
    return smiled_html
