import math
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connection
from django.core.cache import cache
from django.utils import translation
from django.db.models import Q, F, Sum
from django.utils.encoding import smart_str

from forum.util import render_to, paged, build_form, paginate, set_language
from forum.models import Category, Forum, Topic, Post, Profile, Reputation,\
    Report, PrivateMessage, Attachment, PostTracking
from forum.forms import AddPostForm, EditPostForm, UserSearchForm,\
    PostSearchForm, ReputationForm, MailToForm, EssentialsProfileForm,\
    PersonalProfileForm, MessagingProfileForm, PersonalityProfileForm,\
    DisplayProfileForm, PrivacyProfileForm, ReportForm, UploadAvatarForm, CreatePMForm
from forum.markups import mypostmarkup
from forum.templatetags import forum_extras
from forum import settings as forum_settings
from forum.util import urlize, smiles
from forum.index import post_indexer

@render_to('forum/index.html')
def index(request, full=True):
    users_cached = cache.get('users_online', {})
    users_online = users_cached and User.objects.filter(id__in = users_cached.keys()) or []
    guests_cached = cache.get('guests_online', {})
    guest_count = len(guests_cached)
    users_count = len(users_online)

    cats = {}
    forums = {}
    user_groups = request.user.groups.all()
    if request.user.is_anonymous():  # in django 1.1 EmptyQuerySet raise exception
        user_groups = []
    _forums = Forum.objects.filter(
            Q(category__groups__in=user_groups) | \
            Q(category__groups__isnull=True)).select_related('last_post__topic',
                                                            'last_post__user',
                                                            'category')
    for forum in _forums:
        cat = cats.setdefault(forum.category.id,
            {'cat': forum.category, 'forums': []})
        cat['forums'].append(forum)
        forums[forum.id] = forum

    cmpdef = lambda a, b: cmp(a['cat'].position, b['cat'].position)
    cats = sorted(cats.values(), cmpdef)

    to_return = {'cats': cats,
                'posts': Post.objects.count(),
                'topics': Topic.objects.count(),
                'users': User.objects.count(),
                'users_online': users_online,
                'online_count': users_count,
                'guest_count': guest_count,
                'last_user': User.objects.latest('date_joined'),
                }
    if full:
        return to_return
    else:
        to_return['TEMPLATE'] = 'forum/lofi/index.html'
        return to_return

@render_to('forum/moderate.html')
@paged('topics', forum_settings.FORUM_PAGE_SIZE)
def moderate(request, forum_id):
    forum = Forum.objects.get(pk=forum_id)
    topics = forum.topics.order_by('-sticky', '-updated').select_related()
    if request.user.is_superuser or request.user in forum.moderators.all():
        if 'move_topics' in request.POST:
            topic_ids = ','.join([topic for topic in request.POST.getlist('topic_id')])
            return {
                'categories': Category.objects.all(),
                'topic_id': topic_ids,
                'TEMPLATE': 'forum/move_topic.html'
            }
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif 'delete_topics' in request.POST:
            for topic_id in topic_list:
                topic = get_object_or_404(Topic, pk=topic_id)
                topic.delete()
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif 'open_topics' in request.POST:
            for topic_id in topic_list:
                open_topic(request, topic_id)
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif 'close_topics' in request.POST:
            for topic_id in topic_list:
                close_topic(request, topic_id)
            return HttpResponseRedirect(reverse('djangobb:index'))

        return {'forum': forum,
                'topics': topics,
                #'sticky_topics': forum.topics.filter(sticky=True),
                'paged_qs': topics,
                'posts': forum.posts.count(), 
                }
    else:
        raise Http404

@render_to('forum/search_topics.html')
@paged('results', forum_settings.SEARCH_PAGE_SIZE)
def search(request):
    # TODO: move to form
    if 'action' in request.GET:
        action = request.GET['action']
        if action == 'show_24h':
            date = datetime.today() - timedelta(1)
            topics = Topic.objects.filter(created__gte=date).order_by('created')
        elif action == 'show_new':
            #TODO: FIXME
            #must be filter topic.last_post > tracking.last_read and exclude tracking.topics
            topics = Topic.objects.all().order_by('created')
            topics = [topic for topic in topics if forum_extras.has_unreads(topic, request.user)] 
        elif action == 'show_unanswered':
            topics = Topic.objects.filter(post_count=1)
        elif action == 'show_subscriptions':
            topics = Topic.objects.filter(subscribers=request.user)
        elif action == 'show_user':
            user_id = request.GET['user_id']
            posts = Post.objects.filter(user__id=user_id)
            topics = [post.topic for post in posts]
        elif action == 'search':
            keywords = request.GET.get('keywords')
            author = request.GET.get('author')
            forum = request.GET.get('forum')
            search_in = request.GET.get('search_in')
            sort_by = request.GET.get('sort_by')
            sort_dir = request.GET.get('sort_dir')

            if keywords and author:
                if search_in == 'all':
                    if forum == '0':
                        query = 'user:%s AND (topic:%s OR body:%s)' % (author, keywords, keywords)
                    else:
                        query = 'user:%s AND forum:%s AND (topic:%s OR body:%s)' % (author, forum, keywords, keywords)
                elif search_in == 'message':
                    if forum == '0':
                        query = 'user:%s AND body:%s' % (author, keywords)
                    else:
                        query = 'user:%s AND forum:%s AND body:%s' % (author, forum, keywords)
                elif search_in == 'topic':
                    if forum == '0':
                        query = 'user:%s AND topic:%s' % (author, keywords)
                    else:
                        query = 'user:%s AND forum:%s AND topic:%s' % (author, forum, keywords)
            elif keywords:
                if search_in == 'all':
                    if forum == '0':
                        query = 'topic:%s OR body:%s' % (keywords, keywords)
                    else:
                        query = 'forum:%s AND (topic:%s OR body:%s)' % (forum, keywords, keywords)
                elif search_in == 'message':
                    if forum == '0':
                        query = 'body:%s' % (keywords)
                    else:
                        query = 'forum:%s AND body:%s' % (forum, keywords)
                elif search_in == 'topic':
                    if forum == '0':
                        query = 'topic:%s' % (keywords)
                    else:
                        query = 'forum:%s AND topic:%s' % (forum, keywords)
            elif author:
                if forum == '0':
                    query = 'user:%s' % (author)
                else:
                    query = 'forum:%s AND user:%s' % (forum, author)
            else:
                return HttpResponseRedirect(reverse('djangobb:search'))

            order = {'0': 'created',
                     '1': 'user',
                     '2': 'topic',
                     '3': 'forum'}.get(sort_by, 'created')

            if sort_dir == 'DESC':
                order = '-' + order
            posts = post_indexer.search(query).order_by(order)

            if 'topics' in request.GET['show_as']:
                topics = []
                for post in posts:
                    if post.instance.topic not in topics:
                        topics.append(post.instance.topic)
                return {'paged_qs': topics}
            elif 'posts' in request.GET['show_as']:
                return {'paged_qs': posts,
                        'TEMPLATE': 'forum/search_posts.html'
                        }
        return {'paged_qs': topics}
    else:
        form = PostSearchForm()
        return {'categories': Category.objects.all(),
                'form': form,
                'TEMPLATE': 'forum/search_form.html'
                }

@login_required
@render_to('forum/report.html')
def misc(request):
    if 'action' in request.GET:
        action = request.GET['action']
        if action =='markread':
            user = request.user
            PostTracking.objects.filter(user=user).update(last_read=datetime.now(), topics=None)
            return HttpResponseRedirect(reverse('djangobb:index'))

        elif action == 'report':
            if request.GET.get('post_id', ''):
                post_id = request.GET['post_id']
                post = get_object_or_404(Post, id=post_id)
                form = build_form(ReportForm, request, reported_by=request.user, post=post_id)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                    return HttpResponseRedirect(post.get_absolute_url())
                return {'form':form}

    elif 'submit' in request.POST and 'mail_to' in request.GET:
        form = MailToForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=request.GET['mail_to'])
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            user.email_user(subject, body, request.user.email)
            return HttpResponseRedirect(reverse('djangobb:index'))

    elif 'mail_to' in request.GET:
        user = get_object_or_404(User, username=request.GET['mail_to'])
        form = MailToForm()
        return {'form':form,
                'user': user,
               'TEMPLATE': 'forum/mail_to.html'
               }


@render_to('forum/forum.html')
@paged('topics', forum_settings.FORUM_PAGE_SIZE)
def show_forum(request, forum_id, full=True):
    forum = get_object_or_404(Forum, pk=forum_id)
    if not forum.category.has_access(request.user):
        return HttpResponseForbidden()
    topics = forum.topics.order_by('-sticky', '-updated').select_related()
    moderator = request.user.is_superuser or\
        request.user in forum.moderators.all()
    to_return = {'categories': Category.objects.all(),
                'forum': forum,
                'paged_qs': topics,
                'posts': forum.post_count,
                'topics': forum.topic_count,
                'moderator': moderator,
                }
    if full:
        return to_return
    else:
        pages, paginator, paged_list_name = paginate(topics, request, forum_settings.FORUM_PAGE_SIZE)
        to_return.update({'pages': pages,
                        'paginator': paginator, 
                        'topics': paged_list_name,
                        'TEMPLATE': 'forum/lofi/forum.html'
                        })
        del to_return['paged_qs']
        return to_return


@render_to('forum/topic.html')
@paged('posts', forum_settings.TOPIC_PAGE_SIZE)
def show_topic(request, topic_id, full=True):
    topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
    if not topic.forum.category.has_access(request.user):
        return HttpResponseForbidden()
    topic.views = F('views') + 1
    topic.save()

    last_post = topic.last_post

    if request.user.is_authenticated():
        topic.update_read(request.user)

    posts = topic.posts.all().select_related()

    users= set(post.user.id for post in posts)
    profiles = Profile.objects.filter(user__pk__in=users)
    profiles = dict((profile.user_id, profile) for profile in profiles)

    for post in posts:
        post.user.forum_profile = profiles[post.user.id]

    if forum_settings.REPUTATION_SUPPORT:
        replies_list = Reputation.objects.filter(to_user__pk__in=users).values('to_user_id').annotate(sign=Sum('sign')) #values_list buggy?

        replies = {}
        for r in replies_list:
            replies[r['to_user_id']] = r['sign']

        for post in posts:
            post.user.forum_profile.reply_total = replies.get(post.user.id, 0)

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

    highlight_word = request.GET.get('hl', '')
    if full:
        return {'categories': Category.objects.all(),
                'topic': topic,
                'last_post': last_post,
                'form': form,
                'moderator': moderator,
                'subscribed': subscribed,
                'paged_qs': posts,
                'highlight_word': highlight_word,
                }
    else:
        pages, paginator, paged_list_name = paginate(posts, request, forum_settings.TOPIC_PAGE_SIZE)
        return {'categories': Category.objects.all(),
                'topic': topic,
                'pages': pages,
                'paginator': paginator, 
                'posts': paged_list_name,
                'TEMPLATE': 'forum/lofi/topic.html'
                }


@login_required
@render_to('forum/add_post.html')
def add_post(request, forum_id, topic_id):
    forum = None
    topic = None
    posts = None

    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
        if not forum.category.has_access(request.user):
            return HttpResponseForbidden()
    elif topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)
        posts = topic.posts.all().select_related()
        if not topic.forum.category.has_access(request.user):
            return HttpResponseForbidden()
    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())
    
    ip = request.META.get('REMOTE_ADDR', None)
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

@render_to('forum/user.html')
def user(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and user == request.user or request.user.is_superuser:
        if 'section' in request.GET:
            section = request.GET['section']
            if section == 'privacy':
                form = build_form(PrivacyProfileForm, request, instance=user.forum_profile)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                return {'active_menu':'privacy',
                        'profile': user,
                        'form': form,
                        'TEMPLATE': 'forum/profile/profile_privacy.html'
                       }
            elif section == 'display':
                form = build_form(DisplayProfileForm, request, instance=user.forum_profile)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                return {'active_menu':'display',
                        'profile': user,
                        'form': form,
                        'TEMPLATE': 'forum/profile/profile_display.html'
                       }
            elif section == 'personality':
                form = build_form(PersonalityProfileForm, request, instance=user.forum_profile)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                return {'active_menu':'personality',
                        'profile': user,
                        'form': form,
                        'TEMPLATE': 'forum/profile/profile_personality.html'
                        }
            elif section == 'messaging':
                form = build_form(MessagingProfileForm, request, instance=user.forum_profile)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                return {'active_menu':'messaging',
                        'profile': user,
                        'form': form,
                        'TEMPLATE': 'forum/profile/profile_messaging.html'
                       }
            elif section == 'personal':
                form = build_form(PersonalProfileForm, request, instance=user.forum_profile, user=user)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                return {'active_menu':'personal',
                        'profile': user,
                        'form': form,
                        'TEMPLATE': 'forum/profile/profile_personal.html'
                       }
            elif section == 'essentials':
                form = build_form(EssentialsProfileForm, request, instance=user.forum_profile, 
                                  user_view=user, user_request=request.user)
                if request.method == 'POST' and form.is_valid():
                    profile = form.save()
                    set_language(request, profile.language)
                    return HttpResponseRedirect(reverse('djangobb:forum_profile', args=[user.username]))
                    
                return {'active_menu':'essentials',
                        'profile': user,
                        'form': form,
                        'TEMPLATE': 'forum/profile/profile_essentials.html'
                        }
                
        elif 'action' in request.GET:
            action = request.GET['action']
            if action == 'upload_avatar':
                form = build_form(UploadAvatarForm, request, instance=user.forum_profile)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('djangobb:forum_profile', args=[user.username]))
                return {'form': form,
                        'avatar_width': forum_settings.AVATAR_WIDTH,
                        'avatar_height': forum_settings.AVATAR_HEIGHT,
                        'TEMPLATE': 'forum/upload_avatar.html'
                       }
            elif action == 'delete_avatar':
                profile = get_object_or_404(Profile, user=request.user)
                profile.avatar = None
                profile.save()
                return HttpResponseRedirect(reverse('djangobb:forum_profile', args=[user.username]))
         
        else:
            form = build_form(EssentialsProfileForm, request, instance=user.forum_profile, 
                                  user_view=user, user_request=request.user)
            if request.method == 'POST' and form.is_valid():
                profile = form.save()
                set_language(request, profile.language)
                return HttpResponseRedirect(reverse('djangobb:forum_profile', args=[user.username]))
            return {'active_menu':'essentials',
                    'profile': user,
                    'form': form,
                    'TEMPLATE': 'forum/profile/profile_essentials.html'
                   }
            
    else:
        topic_count = Topic.objects.filter(user=user).count()
        if user.forum_profile.post_count < forum_settings.POST_USER_SEARCH and not request.user.is_authenticated():
            return HttpResponseRedirect(reverse('user_signin') + '?next=%s' % request.path)
        return {'profile': user,
                'topic_count': topic_count,
               }

@login_required
@render_to('forum/reputation.html')
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
            return {'form': form,
                    'TEMPLATE': 'forum/reputation_form.html'
                    }
        else:
            raise Http404

    elif request.method == 'POST':
        if 'del_reputation' in request.POST:
            reputation_list = request.POST.getlist('reputation_id')
            for reputation_id in reputation_list:
                    reputation = get_object_or_404(Reputation, pk=reputation_id)
                    reputation.delete()
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif form.is_valid():
            form.save()
            topic_id = request.POST['topic']
            topic = get_object_or_404(Topic, id=topic_id)
            return HttpResponseRedirect(topic.get_absolute_url())
        else:
            raise Http404
    else:
        reputations = Reputation.objects.filter(to_user=user).order_by('-time').select_related()
        return {'reputations': reputations,
                'profile': user.forum_profile,
               }

def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.topic.posts.filter(created__lt=post.created).count() + 1
    page = math.ceil(count / float(forum_settings.TOPIC_PAGE_SIZE))
    url = '%s?page=%d#post-%d' % (reverse('djangobb:topic', args=[post.topic.id]), page, post.id)
    return HttpResponseRedirect(url)

@login_required
@render_to('forum/edit_post.html')
def edit_post(request, post_id):
    from forum.templatetags.forum_extras import forum_editable_by

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
    from forum.templatetags.forum_extras import forum_moderated_by

    topic = Topic.objects.select_related().get(pk=topic_id)

    if forum_moderated_by(topic, request.user):
        deleted = False
        post_list = request.POST.getlist('post')
        for post_id in post_list:
            if not deleted:
                deleted = True
            delete_post(request, post_id)
        if deleted:
            return HttpResponseRedirect(topic.get_absolute_url())

    last_post = topic.posts.latest()

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
def move_topic(request):
    from forum.templatetags.forum_extras import forum_moderated_by
    first_topic = topic_ids = list(request.GET['topic_id'])
    if len(topic_ids) > 1:
        topic_ids = [topic_id for topic_id in topic_ids if topic_id != ',']
    first_topic = topic_ids[0]
    topic = get_object_or_404(Topic, pk=first_topic)
    from_forum = topic.forum_id
    if 'to_forum' in request.GET:
        to_forum = int(request.GET['to_forum'])
        for topic_id in topic_ids:
            topic = get_object_or_404(Topic, pk=topic_id)
            if topic.forum_id != to_forum:
                if forum_moderated_by(topic, request.user):
                    forum = get_object_or_404(Forum, pk=topic.forum_id)
                    topic.forum_id = to_forum
                    forum.post_count -= topic.post_count
                    topic.forum.post_count += topic.post_count
                    forum.topic_count -= 1
                    topic.forum.topic_count += 1
                    topic.forum.save()
                    forum.save()
                    topic.save()
        
        from_forum = get_object_or_404(Forum, pk=from_forum)
        to_forum = get_object_or_404(Forum, pk=to_forum)
        post = Post.objects.filter(topic__forum=from_forum)
        from_forum.last_post = post.latest() if post else None
        to_forum.last_post = Post.objects.filter(topic__forum=to_forum).latest()
        from_forum.save()
        to_forum.save()
        return HttpResponseRedirect(to_forum.get_absolute_url())
    return {'categories': Category.objects.all(),
            'topic_id': topic_ids[0]
            }

@login_required
def stick_topic(request, topic_id):
    from forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if not topic.sticky:
            topic.sticky = True
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def unstick_topic(request, topic_id):
    from forum.templatetags.forum_extras import forum_moderated_by

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
    last_post = post.topic.last_post
    topic = post.topic
    forum = post.topic.forum

    allowed = False
    if request.user.is_superuser or\
        request.user in post.topic.forum.moderators.all() or \
        (post.user == request.user and post == last_post):
        allowed = True

    if not allowed:
        return HttpResponseRedirect(post.get_absolute_url())

    post.delete()
    profile = post.user.forum_profile
    profile.post_count = Post.objects.filter(user=post.user).count()
    profile.save()

    try:
        Topic.objects.get(pk=topic.id)
    except Topic.DoesNotExist:
        #removed latest post in topic
        return HttpResponseRedirect(forum.get_absolute_url())
    else:
        return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def close_topic(request, topic_id):
    from forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if not topic.closed:
            Topic.objects.filter(pk=topic.id).update(closed=True)
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def open_topic(request, topic_id):
    from forum.templatetags.forum_extras import forum_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if topic.closed:
            Topic.objects.filter(pk=topic.id).update(closed=False)
    return HttpResponseRedirect(topic.get_absolute_url())


@render_to('forum/users.html')
@paged('users', forum_settings.USERS_PAGE_SIZE)
def users(request):
    users = User.objects.filter(forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('username')
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
        return HttpResponseRedirect(reverse('djangobb:forum_pm_outbox'))

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
    if not msg.read:
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
        return HttpResponseRedirect(reverse('djangobb:topic', args=[topic.id]))
    else:
        return HttpResponseRedirect(reverse('djangobb:edit_profile'))

@login_required
def add_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.add(request.user)
    return HttpResponseRedirect(reverse('djangobb:topic', args=[topic.id]))

@login_required
def show_attachment(request, hash):
    attachment = get_object_or_404(Attachment, hash=hash)
    file_data = file(attachment.get_absolute_path()).read()
    response = HttpResponse(file_data, mimetype=attachment.content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(attachment.name)
    return response

#TODO: check markup
@render_to('forum/post_preview.html')
def post_preview(request):
    '''Preview for markitup'''
    data = mypostmarkup.markup(request.POST.get('data', ''), auto_urls=False)
    data = urlize(data)
    data = smiles(data)
    return {'data': data}
