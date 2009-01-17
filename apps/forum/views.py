import math
import re
import datetime

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connection
from django.core.cache import cache

from apps.forum.util import render_to, paged, build_form
from apps.forum.models import Category, Forum, Topic, Post, Profile, Read, Reputation, Report, PrivateMessage
from apps.forum.forms import AddPostForm, EditPostForm, UserSearchForm, PostSearchForm, ReputationForm, MailToForm, EssentialsProfileForm, PersonalProfileForm, MessagingProfileForm, PersonalityProfileForm, DisplayProfileForm, PrivacyProfileForm, ReportForm, UploadAvatarForm, CreatePMForm
from apps.forum.markups import mypostmarkup
from apps.forum.templatetags import forum_extras
from apps.forum import settings as forum_settings

@render_to('forum/index.html')
def index(request):
    users_online = []
    
    for user in User.objects.all():
        if cache.get(str(user.id)):
            users_online.append(user)
    guest_count = len(cache._cache) - users_online.__len__()

    cats = {}
    forums = {}

    for forum in Forum.objects.all().select_related():
        cat = cats.setdefault(forum.category.id,
            {'cat': forum.category, 'forums': []})
        cat['forums'].append(forum)
        forums[forum.id] = forum

    cmpdef = lambda a, b: cmp(a['cat'].position, b['cat'].position)
    cats = sorted(cats.values(), cmpdef)

    return {'cats': cats,
            'posts': Post.objects.count(),
            'topics': Topic.objects.count(),
            'users': User.objects.count(),
            'users_online': users_online,
            'online_count': users_online.__len__(),
            'guest_count': guest_count,
            'last_user': User.objects.order_by('-date_joined')[0],
            }

@render_to('forum/moderate.html')
@paged('topics', forum_settings.FORUM_PAGE_SIZE)
def moderate(request, forum_id):
    forum = Forum.objects.get(pk=forum_id)
    topics = forum.topics.filter(sticky=False).select_related()
    if request.user.is_superuser or request.user in forum.moderators.all():
        if 'move_topics' in request.POST:
            for topic in request.POST:
                topic_match = re.match('topic_id\[(\d+)\]', topic)
                
                if topic_match:
                    topic_id = topic_match.group(1)
                    reverse('move_topic', args=[topic_id])
                        
            return HttpResponseRedirect(reverse('index'))
        elif 'delete_topics' in request.POST:
            for topic in request.POST:
                topic_match = re.match('topic_id\[(\d+)\]', reputation)
                    
                if topic_match:
                    topic_id = topic_match.group(1)
                    topic = get_object_or_404(Topic, pk=topic_id)
                    topic.delete()
                        
            return HttpResponseRedirect(reverse('index'))
        elif 'open_topics' in request.POST:
            for topic in request.POST:
                topic_match = re.match('topic_id\[(\d+)\]', topic)
                    
                if topic_match:
                    topic_id = topic_match.group(1)
                    open_topic(request, topic_id)
                        
            return HttpResponseRedirect(reverse('index'))
        elif 'close_topics' in request.POST:
            for topic in request.POST:
                topic_match = re.match('topic_id\[(\d+)\]', topic)
                    
                if topic_match:
                    topic_id = topic_match.group(1)
                    close_topic(request, topic_id)
                        
            return HttpResponseRedirect(reverse('index'))
    
        return {'forum': forum,
                'topics': topics,
                'sticky_topics': forum.topics.filter(sticky=True),
                'paged_qs': topics,
                'posts': forum.posts.count(), 
                }
    else:
        raise Http404

def search(request):
    if 'action' in request.GET:
        if 'show_24h' in request.GET['action']:
            date =  datetime.datetime.today() - datetime.timedelta(1)
            topics = Topic.objects.filter(created__gte=date).order_by('created')
            return render_to_response('forum/search_topics.html', 
                                     {'topics': topics,
                                     }, RequestContext(request))
        elif 'show_new' in request.GET['action']:
            topics = Topic.objects.all().order_by('created')
            topics = [topic for topic in topics if forum_extras.has_unreads(topic, request.user)]
            return render_to_response('forum/search_topics.html', 
                                     {'topics': topics,
                                     }, RequestContext(request))
        elif 'show_unanswered' in request.GET['action']:
            topics = Topic.objects.filter(post_count=1)
            return render_to_response('forum/search_topics.html', 
                                     {'topics': topics,
                                     }, RequestContext(request))
        elif 'show_subscriptions' in request.GET['action']:
            topics = Topic.objects.filter(subscribers=request.user)
            return render_to_response('forum/search_topics.html', 
                                     {'topics': topics,
                                     }, RequestContext(request))
        elif 'show_user' in request.GET['action']:
            user_id = request.GET['user_id']
            posts = Post.objects.filter(user__id=user_id)
            topics = [post.topic for post in posts]
            return render_to_response('forum/search_topics.html', 
                                     {'topics': topics,
                                     }, RequestContext(request))
        elif 'search' in request.GET['action']:
            posts = Post.objects.all()
            form = PostSearchForm(request.GET)
            posts = form.filter(posts)
            topics = [post.topic for post in posts]
            if 'topics' in request.GET['show_as']:
                return render_to_response('forum/search_topics.html', 
                                    {'topics': topics,
                                     }, RequestContext(request))
            elif 'posts' in request.GET['show_as']:
                return render_to_response('forum/search_posts.html', 
                                    {'posts': posts,
                                     }, RequestContext(request))
    else:  
        form = PostSearchForm()
        category = Category.objects.all()[0]
        return render_to_response('forum/search_form.html', 
                                {'categories': Category.objects.all(),
                                'form': form,
                                }, RequestContext(request))
        
@login_required
def misc(request):
    if 'action' in request.GET:
        if 'markread' in request.GET['action']:
            for category in Category.objects.all():
                for topic in category.topics:
                    read, new = Read.objects.get_or_create(user=request.user, topic=topic)
                    if not new:
                        read.time = datetime.datetime.now()
                        read.save()
            return HttpResponseRedirect(reverse('index'))
        
        elif 'report' in request.GET['action']:
            if request.GET['post_id']:
                post_id = request.GET['post_id']
                post = get_object_or_404(Post, id=post_id)
                form = build_form(ReportForm, request, reported_by=request.user, post=post_id)
                if request.POST and form.is_valid():
                    form.save()
                    return HttpResponseRedirect(post.get_absolute_url())
                return render_to_response('forum/report.html', 
                            {'form':form,
                             }, RequestContext(request))
        
    elif 'submit' in request.POST and 'mail_to' in request.GET:
        form = MailToForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=request.GET['mail_to'])
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            user.email_user(subject, body, request.user.email)
            return HttpResponseRedirect(reverse('index'))
        
    elif 'mail_to' in request.GET:
        user = get_object_or_404(User, username=request.GET['mail_to'])
        form = MailToForm()
        return render_to_response('forum/mail_to.html', 
                        {'form':form,
                         'user': user,
                         }, RequestContext(request))

@render_to('forum/forum.html')
@paged('topics', forum_settings.FORUM_PAGE_SIZE)
def show_forum(request, forum_id):
    forum = Forum.objects.get(pk=forum_id)
    topics = forum.topics.filter(sticky=False).select_related()
    moderator = request.user.is_superuser or\
        request.user in forum.moderators.all()

    return {'categories': Category.objects.all(),
            'forum': forum,
            'topics': topics,
            'sticky_topics': forum.topics.filter(sticky=True),
            'paged_qs': topics,
            'posts': forum.posts.count(),
            'topics': forum.topics.count(),
            'moderator': moderator,
            }

    
@render_to('forum/topic.html')
@paged('posts', forum_settings.TOPIC_PAGE_SIZE)
def show_topic(request, topic_id):
    topic = Topic.objects.select_related().get(pk=topic_id)
    topic.views += 1
    topic.save()

    last_post = topic.posts.order_by('-created')[0]

    if request.user.is_authenticated():
        topic.update_read(request.user)

    posts = topic.posts.all().select_related()

    profiles = Profile.objects.filter(user__pk__in=set(x.user.id for x in posts))
    profiles = dict((x.user_id, x) for x in profiles)
    
    for post in posts:
        post.user.forum_profile = profiles[post.user.id]

    initial = {}
    if request.user.is_authenticated():
        initial = {'markup': request.user.forum_profile.markup}
    form = AddPostForm(topic=topic, initial=initial)

    moderator = request.user.is_superuser or\
        request.user in topic.forum.moderators.all()
    if request.user.is_authenticated() and request.user in topic.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    return {'categories': Category.objects.all(),
            'topic': topic,
            'last_post': last_post,
            'form': form,
            'moderator': moderator,
            'subscribed': subscribed,
            'paged_qs': posts,
            }


@login_required
@render_to('forum/add_post.html')
def add_post(request, forum_id, topic_id):
    forum = None
    topic = None
    posts = None

    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    elif topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)
        posts = topic.posts.all().select_related()
    
    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())

    ip = request.META.get('REMOTE_ADDR', '')
    form = build_form(AddPostForm, request, topic=topic, forum=forum,
                      user=request.user, ip=ip,
                      initial={'markup': request.user.forum_profile.markup})

    if 'post_id' in request.GET:
        post_id = request.GET['post_id']
        post = get_object_or_404(Post, pk=post_id)
        form.fields['body'].initial = "[quote=%s]%s[/quote]" % (post.user, post.body)

    if form.is_valid():
        post = form.save();
        return HttpResponseRedirect(post.get_absolute_url())

    return {'form': form,
            'posts': posts,
            'topic': topic,
            'forum': forum,
            }


def user(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and user == request.user or request.user.is_superuser:
        if 'section' in request.GET:
            #if 'admin' in request.GET['section'] and request.user.is_superuser:
            #    form = build_form(AdminProfileForm, request, instance=user.forum_profile)
            #    if request.POST and form.is_valid():
            #        form.save()
            #    return render_to_response('forum/profile/profile_admin.html', 
            #            {'active_menu':'admin',
            #             'profile': user,
            #             #'form': form,
            #             'reports': reports,
            #             }, RequestContext(request))
            if 'privacy' in request.GET['section']:
                form = build_form(PrivacyProfileForm, request, instance=user.forum_profile)
                if request.POST and form.is_valid():
                    form.save()
                return render_to_response('forum/profile/profile_privacy.html', 
                        {'active_menu':'privacy',
                         'profile': user,
                         'form': form,
                         }, RequestContext(request))
            elif 'display' in request.GET['section']:
                form = build_form(DisplayProfileForm, request, instance=user.forum_profile)
                if request.POST and form.is_valid():
                    form.save()
                return render_to_response('forum/profile/profile_display.html', 
                        {'active_menu':'display',
                         'profile': user,
                         'form': form,
                         }, RequestContext(request))
            elif 'personality' in request.GET['section']:
                form = build_form(PersonalityProfileForm, request, instance=user.forum_profile)
                if request.POST and form.is_valid():
                    form.save()
                return render_to_response('forum/profile/profile_personality.html', 
                        {'active_menu':'personality',
                         'profile': user,
                         'form': form,
                         }, RequestContext(request))
            elif 'messaging' in request.GET['section']:
                form = build_form(MessagingProfileForm, request, instance=user.forum_profile)
                if request.POST and form.is_valid():
                    form.save()
                return render_to_response('forum/profile/profile_messaging.html', 
                        {'active_menu':'messaging',
                         'profile': user,
                         'form': form,
                         }, RequestContext(request))
            elif 'personal' in request.GET['section']:
                form = build_form(PersonalProfileForm, request, instance=user.forum_profile, user=user)
                if request.POST and form.is_valid():
                    form.save()
                return render_to_response('forum/profile/profile_personal.html', 
                        {'active_menu':'personal',
                         'profile': user,
                         'form': form,
                         }, RequestContext(request))
            elif 'essentials' in request.GET['section']:
                form = build_form(EssentialsProfileForm, request, instance=user.forum_profile, user=user)
                if request.POST and form.is_valid():
                    form.save()
                return render_to_response('forum/profile/profile_essentials.html', 
                        {'active_menu':'essentials',
                         'profile': user,
                         'form': form,
                         }, RequestContext(request))
                
        elif 'action' in request.GET:
            if 'upload_avatar' in request.GET['action']:
                form = build_form(UploadAvatarForm, request, instance=user.forum_profile)
                if request.POST and form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('forum_profile', args=[user.username]))
                return render_to_response('forum/upload_avatar.html', 
                        {'form': form,
                         'avatar_width': forum_settings.FORUM_AVATAR_WIDTH,
                         'avatar_height': forum_settings.FORUM_AVATAR_HEIGHT,
                         }, RequestContext(request))
            elif 'delete_avatar' in request.GET['action']:
                profile = get_object_or_404(Profile, user=request.user)
                profile.avatar = None
                profile.save()
                return HttpResponseRedirect(reverse('forum_profile', args=[user.username]))
         
        else:
            form = build_form(EssentialsProfileForm, request, instance=user.forum_profile, user=user)
            if request.POST and form.is_valid():
                form.save()
            return render_to_response('forum/profile/profile_essentials.html', 
                    {'active_menu':'essentials',
                     'profile': user,
                     'form': form,
                     }, RequestContext(request))
            
    else:
        topic_count = Topic.objects.filter(user=user).count()
        return render_to_response('forum/user.html', 
                        {'profile': user,
                         'topic_count': topic_count,
                         'reports': reports,
                         }, RequestContext(request))
    

def reputation(request, username):
    user = get_object_or_404(User, username=username)
    form = build_form(ReputationForm, request, from_user=request.user, to_user=user)

    if 'action' in request.GET:
        if 'topic_id' in request.GET:
            sign = 0
            topic_id = request.GET['topic_id']
            form.fields['topic'].initial = topic_id
            if request.GET['action'] == 'plus':
                form.fields['sign'].initial = 1
            elif request.GET['action'] == 'minus':
                form.fields['sign'].initial = -1
            
            return render_to_response('forum/reputation_form.html', 
                    {'form': form,
                     }, RequestContext(request))
        else:
            raise Http404
        
    elif request.POST:
        if 'del_reputation' in request.POST:
            for reputation in request.POST:
                reputation_match = re.match('reputation_id\[(\d+)\]', reputation)
                
                if reputation_match:
                    reputation_id = reputation_match.group(1)
                    reputation = get_object_or_404(Reputation, pk=reputation_id)
                    reputation.delete()
                    
            return HttpResponseRedirect(reverse('index'))
        elif form.is_valid():
            form.save()
            topic_id = request.POST['topic']
            topic = get_object_or_404(Topic, id=topic_id)
            return HttpResponseRedirect(topic.get_absolute_url())
        else:
            raise Http404
        
    else:
        reputations = Reputation.objects.filter(to_user=user).order_by('-time').select_related()
        
        return render_to_response('forum/reputation.html', 
                {'reputations': reputations,
                'profile': user.forum_profile,
                }, RequestContext(request))


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.topic.posts.filter(created__lt=post.created).count() + 1
    page = math.ceil(count / float(forum_settings.TOPIC_PAGE_SIZE))
    url = '%s?page=%d#post-%d' % (reverse('topic', args=[post.topic.id]), page, post.id)
    return HttpResponseRedirect(url)
   
@login_required
@render_to('forum/edit_post.html')
def edit_post(request, post_id):
    from apps.forum.templatetags.forum_extras import forum_editable_by

    post = get_object_or_404(Post, pk=post_id)
    topic = post.topic
    if not forum_editable_by(post, request.user):
        return HttpResponseRedirect(post.get_absolute_url())
    form = build_form(EditPostForm, request, topic=topic, instance=post)
    if form.is_valid():
        post = form.save()
        return HttpResponseRedirect(post.get_absolute_url())

    return {'form': form,
            'post': post,
            }

@login_required
@render_to('forum/delete_posts.html')
@paged('posts', forum_settings.TOPIC_PAGE_SIZE)
def delete_posts(request, topic_id):
    from apps.forum.templatetags.forum_extras import forum_moderated_by

    topic = Topic.objects.select_related().get(pk=topic_id)
    topic.views += 1
    topic.save()
    
    if forum_moderated_by(topic, request.user):
        deleted = False
        for post in request.POST:
            if not deleted:
                deleted = True
            post_id = re.match('post\[(\d+)\]', post).group(1)
            delete_post(request, post_id)
        if deleted:
            return HttpResponseRedirect(topic.get_absolute_url())

    last_post = topic.posts.order_by('-created')[0]

    if request.user.is_authenticated():
        topic.update_read(request.user)

    posts = topic.posts.all().select_related()

    profiles = Profile.objects.filter(user__pk__in=set(x.user.id for x in posts))
    profiles = dict((x.user_id, x) for x in profiles)
    
    for post in posts:
        post.user.forum_profile = profiles[post.user.id]

    initial = {}
    if request.user.is_authenticated():
        initial = {'markup': request.user.forum_profile.markup}
    form = AddPostForm(topic=topic, initial=initial)

    moderator = request.user.is_superuser or\
        request.user in topic.forum.moderators.all()
    if request.user.is_authenticated() and request.user in topic.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    return {
            'topic': topic,
            'last_post': last_post,
            'form': form,
            'moderator': moderator,
            'subscribed': subscribed,
            'paged_qs': posts,
            }

@login_required
@render_to('forum/move_topic.html')
def move_topic(request, topic_id):
    from apps.forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if 'to_forum' in request.GET:
            topic.forum_id = request.GET['to_forum']
            topic.save()
            return HttpResponseRedirect(topic.forum.get_absolute_url())
    return {'categories': Category.objects.all(),
            }

@login_required
def stick_topic(request, topic_id):
    from apps.forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if not topic.sticky:
            topic.sticky = True
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def unstick_topic(request, topic_id):
    from apps.forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if topic.sticky:
            topic.sticky = False
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
@render_to('forum/delete_post.html')
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    last_post = post.topic.posts.order_by('-created')[0]
    topic = post.topic

    allowed = False
    if request.user.is_superuser or\
        request.user in post.topic.forum.moderators.all() or \
        (post.user == request.user and post == last_post):
        allowed = True

    if not allowed:
        return HttpResponseRedirect(post.get_absolute_url())

    topic = post.topic
    forum = post.topic.forum
    topic.post_count -= 1
    forum.post_count -= 1
    forum.save()
    topic.save()
    post.delete()

    try:
        Topic.objects.get(pk=topic.id)
    except Topic.DoesNotExist:
        return HttpResponseRedirect(forum.get_absolute_url())
    else:
        return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def close_topic(request, topic_id):
    from apps.forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if not topic.closed:
            topic.closed = True
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def open_topic(request, topic_id):
    from apps.forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if topic.closed:
            topic.closed = False
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@render_to('forum/users.html')
@paged('users', forum_settings.USERS_PAGE_SIZE)
def users(request):
    users = User.objects.order_by('username')
    form = UserSearchForm(request.GET)
    users = form.filter(users)
    return {'paged_qs': users,
            'form': form,
            }
    
@login_required
@render_to('forum/pm/create_pm.html')
def create_pm(request):
    recipient = request.GET.get('recipient', '')
    form = build_form(CreatePMForm, request, user=request.user,
                      initial={'markup': request.user.forum_profile.markup,
                               'recipient': recipient})

    if form.is_valid():
        post = form.save();
        return HttpResponseRedirect(reverse('forum_pm_outbox'))

    return {'active_menu':'create',
            'form': form,
            }

@login_required
@render_to('forum/pm/outbox.html')
def pm_outbox(request):
    messages = PrivateMessage.objects.filter(src_user=request.user)
    return {'active_menu':'outbox',
            'messages': messages,
            }

@login_required
@render_to('forum/pm/inbox.html')
def pm_inbox(request):
    messages = PrivateMessage.objects.filter(dst_user=request.user)
    return {'active_menu':'inbox',
            'messages': messages,
            }

@login_required
@render_to('forum/pm/message.html')
def show_pm(request, pm_id):
    msg = get_object_or_404(PrivateMessage, pk=pm_id)
    if not request.user in [msg.dst_user, msg.src_user]:
        return HttpRedirectException('/')
    if request.user == msg.dst_user:
        inbox = True
        post_user = msg.src_user
    else:
        inbox = False
        post_user = msg.dst_user
    msg.read = True
    msg.save()
    return {'msg': msg,
            'inbox': inbox,
            'post_user': post_user,
            }


@login_required
def delete_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.remove(request.user)
    if 'from_topic' in request.GET:
        return HttpResponseRedirect(reverse('topic', args=[topic.id]))
    else:
        return HttpResponseRedirect(reverse('edit_profile'))


@login_required
def add_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.add(request.user)
    return HttpResponseRedirect(reverse('topic', args=[topic.id]))

def post_preview(request):
    '''Preview for markitup'''
    html = '<link type="text/css" rel="stylesheet" href="%sforum/css/hljs_styles/phpbb_blue.css" /><p>' % settings.MEDIA_URL
    return HttpResponse(html+mypostmarkup.markup(request.POST.get('data', ''), auto_urls=False))

