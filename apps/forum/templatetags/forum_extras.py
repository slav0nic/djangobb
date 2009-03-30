# -*- coding: utf-8
from datetime import datetime, timedelta
import urllib
try:
    from hashlib import md5
except ImportError:
    import md5
    md5 = md5.new

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

from forum.models import Forum, Topic, Post, Read, PrivateMessage, Report
from forum.unread import cache_unreads
from forum import settings as forum_settings


register = template.Library()

# TODO:
# * rename all tags with forum_ prefix

@register.filter
def profile_link(user):
    data = u'<a href="%s">%s</a>' % (\
        reverse('forum_profile', args=[user.username]), user.username)
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
        delta = datetime.now() - time
        today = datetime.now().replace(hour=0, minute=0, second=0)
        yesterday = today - timedelta(days=1)
        
        if time > today:
            return u'Сегодня %s' % time.strftime('%H:%M:%S')
        elif time > yesterday:
            return u'Вчера %s' % time.strftime('%H:%M:%S')
        else:
            return time.strftime('%Y-%m-%d %H:%M:%S')

# TODO: this old code requires refactoring
@register.inclusion_tag('forum/pagination.html',takes_context=True)
def pagination(context, adjacent_pages=1):
    """
    Return the list of A tags with links to pages.
    """

    page_list = range(
        max(1,context['page'] - adjacent_pages),
        min(context['pages'],context['page'] + adjacent_pages) + 1)
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
    get_params = '&'.join(['%s=%s' % (x[0],','.join(x[1])) for x in
        context['request'].GET.iteritems() if (not x[0] == 'page' and not x[0] == 'per_page')])
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

    now = datetime.now()
    delta = timedelta(seconds=forum_settings.READ_TIMEOUT)

    if not user.is_authenticated():
        return False
    else:
        if isinstance(topic, Topic):
            if (now - delta > topic.updated):
                return False
            else:
                if hasattr(topic, '_read'):
                    read = topic._read
                else:
                    try:
                        read = Read.objects.get(user=user, topic=topic)
                    except Read.DoesNotExist:
                        read = None

                if read is None:
                    return True
                else:
                    return topic.updated > read.time
        else:
            raise Exception('Object should be a topic')


@register.filter
def forum_setting(name):
    return mark_safe(getattr(forum_settings, name, 'NOT DEFINED'))


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
def forum_unreads(qs, user):
    return cache_unreads(qs, user)


@register.filter
def forum_authority(user):
    posts = user.forum_profile.post_count
    if posts >= forum_settings.FORUM_STEP_10: 
        return mark_safe('<img src="%sforum/img/authority/vote10.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_9: 
        return mark_safe('<img src="%sforum/img/authority/vote9.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_8: 
        return mark_safe('<img src="%sforum/img/authority/vote8.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_7: 
        return mark_safe('<img src="%sforum/img/authority/vote7.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_6: 
        return mark_safe('<img src="%sforum/img/authority/vote6.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_5: 
        return mark_safe('<img src="%sforum/img/authority/vote5.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_4: 
        return mark_safe('<img src="%sforum/img/authority/vote4.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_3: 
        return mark_safe('<img src="%sforum/img/authority/vote3.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_2: 
        return mark_safe('<img src="%sforum/img/authority/vote2.gif" alt="" >' % (settings.MEDIA_URL))
    elif posts >= forum_settings.FORUM_STEP_1: 
        return mark_safe('<img src="%sforum/img/authority/vote1.gif" alt="" >' % (settings.MEDIA_URL))
    else:
        return mark_safe('<img src="%sforum/img/authority/vote0.gif" alt="" >' % (settings.MEDIA_URL))

@register.filter
def online(user):
    return cache.get(str(user.id))

@register.filter
def pm_unreads(user):
    return PrivateMessage.objects.filter(dst_user=user, read=False).count()

@register.simple_tag
def new_reports():
    return Report.objects.filter(zapped=False).count()

@register.simple_tag
def gravatar(email):
    if forum_settings.GRAVATAR_SUPPORT:
        size = max(forum_settings.AVATAR_WIDTH, forum_settings.AVATAR_HEIGHT)
        url = "http://www.gravatar.com/avatar.php?"
        url += urllib.urlencode({
            'gravatar_id': md5(email.lower()).hexdigest(),
            'size': size,
            'default': forum_settings.GRAVATAR_DEFAULT,
        })
        return url
    else:
        return ''
