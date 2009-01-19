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

def render_to(template_path):
    """
    Expect the dict from view. Render returned dict with
    RequestContext.
    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            kwargs = {'context_instance': RequestContext(request)}
            if 'MIME_TYPE' in output:
                kwargs['mimetype'] = output.pop('MIME_TYPE')
            if 'TEMPLATE' in output:
                template = output.pop('TEMPLATE')
            else:
                template = template_path
            return render_to_response(template, output, **kwargs)
        return wrapper

    return decorator

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

def urlize(data):
    """
    Urlize plain text links in the HTML contents.
   
    Do not urlize content of A and CODE tags.
    """
    
    class URLizeHTMLParser(HTMLParser):
    
        def __init__(self):
            HTMLParser.__init__(self)
            self.is_link = False
            self.urlized_html = []
            
        def handle_starttag(self, tag, attrs):
            self.urlized_html.append('<%s%s>' % (tag, self.__html_attrs(attrs)))
            if tag in ('a', 'code'):
                self.is_link = True
    
        def handle_data(self, data):
            if not self.is_link:
                data = django_urlize(data)
            self.urlized_html.append(data)
    
        def handle_startendtag(self, tag, attrs):
            self.urlized_html.append('<%s%s/>' % (tag, self.__html_attrs(attrs))) 
    
        def handle_endtag(self, tag):
            self.is_link = False
            self.urlized_html.append('</%s>' % (tag))
    
        def __html_attrs(self, attrs):
            _attrs = ''
            if attrs:
                _attrs = ' %s' % (' '.join([('%s="%s"' % (k,v)) for k,v in attrs]))
            return _attrs
    
        def feed(self, data):
            HTMLParser.feed(self, data)
            self.urlized_html = ''.join(self.urlized_html)
        
    parser = URLizeHTMLParser()
    parser.feed(data)
    urlized_html = parser.urlized_html
    parser.close()
    return urlized_html

def smiles(data):
    # TODO: code refactoring; ignore smiles in tag [code]
    data = re.compile(r':\)').sub(forum_settings.EMOTION_SMILE, data)
    data = re.compile(r'=\)').sub(forum_settings.EMOTION_SMILE, data)
    data = re.compile(r':\|').sub(forum_settings.EMOTION_NEUTRAL, data)
    data = re.compile(r'=\|').sub(forum_settings.EMOTION_NEUTRAL, data)
    data = re.compile(r':\(').sub(forum_settings.EMOTION_SAD, data)
    data = re.compile(r'=\(').sub(forum_settings.EMOTION_SAD, data)
    data = re.compile(r':D').sub(forum_settings.EMOTION_BIG_SMILE, data)
    data = re.compile(r'=D').sub(forum_settings.EMOTION_BIG_SMILE, data)
    data = re.compile(r':o').sub(forum_settings.EMOTION_YIKES, data)
    data = re.compile(r':O').sub(forum_settings.EMOTION_YIKES, data)
    data = re.compile(r';\)').sub(forum_settings.EMOTION_WINK, data)
    data = re.compile(r'(?<!http):/').sub(forum_settings.EMOTION_HMM, data)
    data = re.compile(r':P').sub(forum_settings.EMOTION_TONGUE, data)
    data = re.compile(r':lol:').sub(forum_settings.EMOTION_LOL, data)
    data = re.compile(r':mad:').sub(forum_settings.EMOTION_MAD, data)
    data = re.compile(r':rolleyes:').sub(forum_settings.EMOTION_ROLL, data)
    data = re.compile(r':cool:').sub(forum_settings.EMOTION_COOL, data)
    return data

