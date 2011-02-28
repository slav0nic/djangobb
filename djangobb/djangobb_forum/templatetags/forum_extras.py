# -*- coding: utf-8
from datetime import datetime, timedelta
import urllib

from django import template
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.utils.safestring import mark_safe
from django.template import RequestContext
from django.utils.encoding import smart_unicode
from django.db import settings
from django.utils.html import escape
from django.utils.translation import ugettext as _
from django.utils import dateformat
from django.utils.hashcompat import md5_constructor
from django.contrib.humanize.templatetags.humanize import naturalday

from djangobb_forum.models import Forum, Topic, Post, PostTracking, Report
from djangobb_forum import settings as forum_settings

if forum_settings.PM_SUPPORT:
    from messages.models import inbox_count_for

register = template.Library()

# TODO:
# * rename all tags with forum_ prefix

@register.filter
def profile_link(user):
    data = u'<a href="%s">%s</a>' % (\
        reverse('djangobb:forum_profile', args=[user.username]), user.username)
    return mark_safe(data)


@register.tag
def forum_time(parser, token):
    try:
        tag, time = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('forum_time requires single argument')
    else:
        return ForumTimeNode(time)


class ForumTimeNode(template.Node):
    def __init__(self, time):
        self.time = template.Variable(time)

    def render(self, context):
        time = self.time.resolve(context)
        formated_time = u'%s %s' % (naturalday(time), time.strftime('%H:%M:%S'))
        formated_time = mark_safe(formated_time)
        return formated_time


# TODO: this old code requires refactoring
@register.inclusion_tag('forum/pagination.html',takes_context=True)
def pagination(context, adjacent_pages=1):
    """
    Return the list of A tags with links to pages.
    """

    page_list = range(
        max(1, context['page'] - adjacent_pages),
        min(context['pages'], context['page'] + adjacent_pages) + 1)
    lower_page = None
    higher_page = None

    if not 1 == context['page']:
        lower_page = context['page'] - 1

    if not 1 in page_list:
        page_list.insert(0,1)
        if not 2 in page_list:
            page_list.insert(1,'.')

    if not context['pages'] == context['page']:
        higher_page = context['page'] + 1

    if not context['pages'] in page_list:
        if not context['pages'] - 1 in page_list:
            page_list.append('.')
        page_list.append(context['pages'])
    get_params = '&'.join(['%s=%s' % (x[0], x[1]) for x in
        context['request'].GET.iteritems() if (x[0] != 'page' and x[0] != 'per_page')])
    if get_params:
        get_params = '?%s&' % get_params
    else:
        get_params = '?'

    return {
        'get_params': get_params,
        'lower_page': lower_page,
        'higher_page': higher_page,
        'page': context['page'],
        'pages': context['pages'],
        'page_list': page_list,
        'per_page': context['per_page'],
        }


@register.inclusion_tag('forum/lofi/pagination.html',takes_context=True)
def lofi_pagination(context):
    page_list = range(1, context['pages'] + 1)
    paginator = context['paginator']
    
    get_params = '&'.join(['%s=%s' % (x[0],','.join(x[1])) for x in
        context['request'].GET.iteritems() if (not x[0] == 'page' and not x[0] == 'per_page')])
    if get_params:
        get_params = '?%s&' % get_params
    else:
        get_params = '?'
        
    return {
            'get_params': get_params,
            'page_list': page_list,
            'paginator': paginator,
            } 


@register.simple_tag
def link(object, anchor=u''):
    """
    Return A tag with link to object.
    """

    url = hasattr(object,'get_absolute_url') and object.get_absolute_url() or None
    anchor = anchor or smart_unicode(object)
    return mark_safe('<a href="%s">%s</a>' % (url, escape(anchor)))


@register.simple_tag
def lofi_link(object, anchor=u''):
    """
    Return A tag with lofi_link to object.
    """

    url = hasattr(object,'get_absolute_url') and object.get_absolute_url() or None   
    anchor = anchor or smart_unicode(object)
    return mark_safe('<a href="%slofi">%s</a>' % (url, escape(anchor)))


@register.filter
def has_unreads(topic, user):
    """
    Check if topic has messages which user didn't read.
    """
    if not user.is_authenticated() or\
        (user.posttracking.last_read is not None and\
         user.posttracking.last_read > topic.last_post.created):
            return False
    else:
        if isinstance(user.posttracking.topics, dict):
            if topic.last_post.id > user.posttracking.topics.get(str(topic.id), 0):
                return True
            else:
                return False
        return True


@register.filter
def forum_moderated_by(topic, user):
    """
    Check if user is moderator of topic's forum.
    """

    return user.is_superuser or user in topic.forum.moderators.all()


@register.filter
def forum_editable_by(post, user):
    """
    Check if the post could be edited by the user.
    """

    if user.is_superuser:
        return True
    if post.user == user:
        return True
    if user in post.topic.forum.moderators.all():
        return True
    return False


@register.filter
def forum_posted_by(post, user):
    """
    Check if the post is writed by the user.
    """

    return post.user == user


@register.filter
def forum_equal_to(obj1, obj2):
    """
    Check if objects are equal.
    """

    return obj1 == obj2


@register.filter
def forum_authority(user):
    posts = user.forum_profile.post_count
    if posts >= forum_settings.AUTHORITY_STEP_10: 
        return mark_safe('<img src="%sforum/img/authority/vote10.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_9: 
        return mark_safe('<img src="%sforum/img/authority/vote9.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_8: 
        return mark_safe('<img src="%sforum/img/authority/vote8.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_7: 
        return mark_safe('<img src="%sforum/img/authority/vote7.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_6: 
        return mark_safe('<img src="%sforum/img/authority/vote6.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_5: 
        return mark_safe('<img src="%sforum/img/authority/vote5.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_4: 
        return mark_safe('<img src="%sforum/img/authority/vote4.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_3: 
        return mark_safe('<img src="%sforum/img/authority/vote3.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_2: 
        return mark_safe('<img src="%sforum/img/authority/vote2.gif" alt="" />' % (settings.MEDIA_URL))
    elif posts >= forum_settings.AUTHORITY_STEP_1: 
        return mark_safe('<img src="%sforum/img/authority/vote1.gif" alt="" />' % (settings.MEDIA_URL))
    else:
        return mark_safe('<img src="%sforum/img/authority/vote0.gif" alt="" />' % (settings.MEDIA_URL))

    
@register.filter
def online(user):
    return cache.get(str(user.id))


@register.filter
def pm_unreads(user):
    if forum_settings.PM_SUPPORT:
        return inbox_count_for(user)
    return None

@register.filter
def attachment_link(attach):
    from django.template.defaultfilters import filesizeformat
    if attach.content_type in ['image/png', 'image/gif', 'image/jpeg']:
        img = '<img src="%sforum/img/attachment/image.png" alt="attachment" />' % (settings.MEDIA_URL)
    elif attach.content_type in ['application/x-tar', 'application/zip']:
        img = '<img src="%sforum/img/attachment/compress.png" alt="attachment" />' % (settings.MEDIA_URL)
    elif attach.content_type in ['text/plain']:
        img = '<img src="%sforum/img/attachment/text.png" alt="attachment" />' % (settings.MEDIA_URL)
    elif attach.content_type in ['application/msword']:
        img = '<img src="%sforum/img/attachment/doc.png" alt="attachment" />' % (settings.MEDIA_URL)
    else:
        img = '<img src="%sforum/img/attachment/unknown.png" alt="attachment" />' % (settings.MEDIA_URL)
    attachment = '%s <a href="%s">%s</a> (%s)' % (img, attach.get_absolute_url(), attach.name, filesizeformat(attach.size))
    return mark_safe(attachment)


@register.simple_tag
def new_reports():
    return Report.objects.filter(zapped=False).count()


@register.simple_tag
def gravatar(email):
    if forum_settings.GRAVATAR_SUPPORT:
        size = max(forum_settings.AVATAR_WIDTH, forum_settings.AVATAR_HEIGHT)
        url = "http://www.gravatar.com/avatar/%s?" % md5_constructor(email.lower()).hexdigest()
        url += urllib.urlencode({
            'size': size,
            'default': forum_settings.GRAVATAR_DEFAULT,
        })
        return url.replace('&', '&amp;')
    else:
        return ''

@register.simple_tag
def set_theme_style(user):
    theme_style = ''
    selected_theme = '' 
    if user.is_authenticated():
        selected_theme = user.forum_profile.theme
        theme_style = '<link rel="stylesheet" type="text/css" href="%(media_url)sforum/themes/%(theme)s/style.css" />' 
    else:
        theme_style = '<link rel="stylesheet" type="text/css" href="%(media_url)sforum/themes/default/style.css" />'
        
    return theme_style % dict(
        media_url=settings.MEDIA_URL,
        theme=selected_theme
    )

@register.simple_tag
def set_markup_editor(user, markup=None):
    markup_style = '' 
    if user.is_authenticated():
        markup_style = '''
            <link rel="stylesheet" type="text/css" href="%(media_url)sforum/js/markitup/skins/markitup/style.css" />
            <link rel="stylesheet" type="text/css" href="%(media_url)sforum/js/markitup/sets/%(markup)s/style.css" />
            <script type="text/javascript" src="%(media_url)sforum/js/markitup/jquery.markitup.pack.js"></script>
            <script type="text/javascript" src="%(media_url)sforum/js/markitup/sets/%(markup)s/set.js"></script>
            <script type="text/javascript" src="%(media_url)sforum/js/markup/%(markup)s/board.js"></script>
        ''' % dict(
            media_url=settings.MEDIA_URL,
            markup=markup if markup else user.forum_profile.markup
        )
    return markup_style
