# coding: utf-8

import math
import re
import urllib2
import httpagentparser
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import transaction, connection
from django.db.models import Q, F
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from haystack.query import SearchQuerySet, SQ

from djangobb_forum import settings as forum_settings
from djangobb_forum.forms import AddPostForm, EditPostForm, UserSearchForm, \
    PostSearchForm, ReputationForm, MailToForm, PersonalityProfileForm, \
    VotePollForm, ReportForm, VotePollForm, PollForm
from djangobb_forum.models import Category, Forum, Topic, Post, Reputation, \
    Report, Attachment, PostTracking
from djangobb_forum.templatetags import forum_extras
from djangobb_forum.templatetags.forum_extras import forum_moderated_by
from djangobb_forum.util import build_form, paginate, set_language, smiles, convert_text_to_html, UnapprovedImageError, can_close_topic

from lib.utils import get_client_ip


def simple_user_agent(request):
    """
    Utility function to show the user agent in a human-readable form. Uses
    simple parser from httpagentparser and removes the punctuation from that.
    """
    return ', '.join(httpagentparser.simple_detect(request.META.get('HTTP_USER_AGENT', tuple())))

def index(request, full=True):
    users_cached = cache.get('djangobb_users_online', {})
    users_online = users_cached and User.objects.filter(id__in=users_cached.keys()) or []
    guests_cached = cache.get('djangobb_guests_online', {})
    guest_count = len(guests_cached)
    users_count = len(users_online)
    online_truncated = users_count > forum_settings.MAX_ONLINE
    if online_truncated:
        users_online = users_online[:forum_settings.MAX_ONLINE]

    _forums = Forum.objects.select_related('last_post__topic', 'last_post__user', 'category')
    user = request.user
    if not user.is_superuser:
        user_groups = user.groups.all() or [] # need 'or []' for anonymous user otherwise: 'EmptyManager' object is not iterable
        _forums = _forums.filter(Q(category__groups__in=user_groups) | Q(category__groups__isnull=True))

    cats = {}
    forums = {}
    for forum in _forums:
        cat = cats.setdefault(forum.category.id,
            {'id': forum.category.id, 'cat': forum.category, 'forums': []})
        cat['forums'].append(forum)
        forums[forum.id] = forum

    cmpdef = lambda a, b: cmp(a['cat'].position, b['cat'].position)
    cats = sorted(cats.values(), cmpdef)

    to_return = {'cats': cats,
                'users_online': users_online,
                'online_count': users_count,
                'online_truncated': online_truncated,
                'guest_count': guest_count,
                }
    if full:
        return render(request, 'djangobb_forum/index.html', to_return)
    else:
        return render(request, 'djangobb_forum/mobile/index.html', to_return)


@transaction.commit_on_success
def moderate(request, forum_id):
    forum = get_object_or_404(Forum, pk=forum_id)
    topics = forum.topics.order_by('-sticky', '-updated').select_related()
    if request.user.is_superuser or request.user in forum.moderators.all():
        topic_ids = request.POST.getlist('topic_id')
        if 'move_topics' in request.POST:
            return render(request, 'djangobb_forum/move_topic.html', {
                'categories': Category.objects.all(),
                'topic_ids': topic_ids,
                'exclude_forum': forum,
            })
        elif 'delete_topics' in request.POST:
            for topic_id in topic_ids:
                topic = get_object_or_404(Topic, pk=topic_id)
                topic.delete()
            messages.success(request, _("Topics deleted."))
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif 'open_topics' in request.POST:
            for topic_id in topic_ids:
                open_close_topic(request, topic_id, 'o')
            messages.success(request, _("Topics opened."))
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif 'close_topics' in request.POST:
            for topic_id in topic_ids:
                open_close_topic(request, topic_id, 'c')
            messages.success(request, _("Topics closed."))
            return HttpResponseRedirect(reverse('djangobb:index'))

        return render(request, 'djangobb_forum/moderate.html', {'forum': forum,
                'topics': topics,
                #'sticky_topics': forum.topics.filter(sticky=True),
                'posts': forum.posts.count(),
                })
    else:
        raise Http404

@transaction.commit_on_success
def reports(request):
    if request.user.is_superuser or request.user.has_perm('djangobb_forum.change_report'):
        if 'action' in request.GET:
            zap_report_id = int(request.POST['id'])
            zap_report = get_object_or_404(Report, pk=zap_report_id)
            if request.GET['action'] == 'zap':
                zap_report.zapped_by = request.user
                zap_report.zapped = True
            elif request.GET['action'] == 'unzap':
                zap_report.zapped_by = None
                zap_report.zapped = False
            zap_report.save()
        new_reports = Report.objects.filter(zapped = False).order_by('-created')
        zapped_reports = Report.objects.filter(zapped = True).order_by('-created')[:10]

        return render(request, 'djangobb_forum/reports.html', {'new_reports' : new_reports, 'zapped_reports' : zapped_reports})
    else:
        raise Http404

def search(request, full=True):
    # TODO: used forms in every search type
    template_dir = 'djangobb_forum/' if full else 'djangobb_forum/mobile/'

    def _render_search_form(form=None):
        # TODO: remove 'in' clause from following query
        categories_with_forums = Category.objects.prefetch_related('forums')
        return render(request, template_dir + 'search_form.html', {
            'categories': categories_with_forums,
            'form': form,
        })

    if not 'action' in request.GET:
        return _render_search_form(form=PostSearchForm())

    if request.GET.get("show_as") == "posts":
        show_as_posts = True
        template_name = template_dir + 'search_posts.html'
    else:
        show_as_posts = False
        template_name = template_dir + 'search_topics.html'

    context = {}

    # Create 'user viewable' pre-filtered topics/posts querysets
    viewable_category = Category.objects.all()
    topics = Topic.objects.all().order_by("-last_post__created")
    posts = Post.objects.all().order_by('-created')
    user = request.user
    if not user.is_superuser:
        user_groups = user.groups.all() or [] # need 'or []' for anonymous user otherwise: 'EmptyManager' object is not iterable
        viewable_category = viewable_category.filter(Q(groups__in=user_groups) | Q(groups__isnull=True))

        topics = Topic.objects.filter(forum__category__in=viewable_category) \
            .select_related('last_post', 'last_post__user', 'user', 'forum')
        posts = Post.objects.filter(topic__forum__category__in=viewable_category)

    base_url = None
    _generic_context = True

    context["user"] = user

    action = request.GET['action']
    if action == 'show_24h':
        date = timezone.now() - timedelta(days=1)
        if show_as_posts:
            context["posts"] = posts.filter(Q(created__gte=date) | Q(updated__gte=date))
        else:
            context["topics"] = topics.filter(Q(last_post__created__gte=date) | Q(last_post__updated__gte=date))
        _generic_context = False
    elif action == 'show_new':
        if not user.is_authenticated():
            raise Http404("Search 'show_new' not available for anonymous user.")
        try:
            last_read = PostTracking.objects.get(user=user).last_read
        except PostTracking.DoesNotExist:
            last_read = None

        if last_read:
            if show_as_posts:
                context["posts"] = posts.filter(Q(created__gte=last_read) | Q(updated__gte=last_read))
            else:
                context["topics"] = topics.filter(Q(last_post__created__gte=last_read) | Q(last_post__updated__gte=last_read))
            _generic_context = False
        else:
            topic_ids = [topic.id for topic in topics[:forum_settings.SEARCH_PAGE_SIZE] if forum_extras.has_unreads(topic, user)]
            topics = Topic.objects.filter(id__in=topic_ids)
    elif action == 'show_unanswered':
        topics = topics.filter(post_count=1)
    elif action == 'show_subscriptions':
        topics = topics.filter(subscribers__id=user.id)
    elif action == 'show_user':
        # Show all posts from user or topics started by user
        if not user.is_authenticated():
            raise Http404("Search 'show_user' not available for anonymous user.")

        if user.is_staff:
            user_id = request.GET.get("user_id", user.id)
            user_id = int(user_id)
            if user_id != user.id:
                search_user = User.objects.get(id=user_id)
                messages.info(request, "Filter by user '%s'." % search_user.username)
        else:
            user_id = user.id

        if show_as_posts:
            posts = posts.filter(user__id=user_id)
        else:
            # show as topic
            topics = topics.filter(posts__user__id=user_id).order_by("-last_post__created").distinct()

        base_url = "?action=show_user&user_id=%s&show_as=" % user_id
    elif action == 'search':
        form = PostSearchForm(request.GET)
        if not form.is_valid():
            return _render_search_form(form)

        keywords = form.cleaned_data['keywords']
        author = form.cleaned_data['author']
        forum = form.cleaned_data['forum']
        search_in = form.cleaned_data['search_in']
        sort_by = form.cleaned_data['sort_by']
        sort_dir = form.cleaned_data['sort_dir']

        query = SearchQuerySet().models(Post)

        if author:
            query = query.filter(author__username=author)

        if forum != u'0':
            query = query.filter(forum__id=forum)

        if keywords:
            if search_in == 'all':
                query = query.filter(SQ(topic=keywords) | SQ(text=keywords))
            elif search_in == 'message':
                query = query.filter(text=keywords)
            elif search_in == 'topic':
                query = query.filter(topic=keywords)

        order = {'0': 'created',
                 '1': 'author',
                 '2': 'topic',
                 '3': 'forum'}.get(sort_by, 'created')
        if sort_dir == 'DESC':
            order = '-' + order

        posts = query.order_by(order)

        if not show_as_posts:
            # TODO: We have here a problem to get a list of topics without double entries.
            # Maybe we must add a search index over topics?

            # Info: If whoosh backend used, setup HAYSTACK_ITERATOR_LOAD_PER_QUERY
            #    to a higher number to speed up
            post_pks = posts.values_list("pk", flat=True)
            context["topics"] = topics.filter(posts__in=post_pks).distinct()
        else:
            # FIXME: How to use the pre-filtered query from above?
            posts = posts.filter(topic__forum__category__in=viewable_category)
            context["posts"] = posts

        get_query_dict = request.GET.copy()
        get_query_dict.pop("show_as")
        base_url = "?%s&show_as=" % get_query_dict.urlencode()
        _generic_context = False

    if _generic_context:
        if show_as_posts:
            context["posts"] = posts.filter(topic__in=topics).order_by('-created')
        else:
            context["topics"] = topics

    if base_url is None:
        base_url = "?action=%s&show_as=" % action

    if show_as_posts:
        context["as_topic_url"] = base_url + "topics"
        post_count = context["posts"].count()
        messages.success(request, _("Found %i posts.") % post_count)
    else:
        context["as_post_url"] = base_url + "posts"
        topic_count = context["topics"].count()
        messages.success(request, _("Found %i topics.") % topic_count)

    return render(request, template_name, context)




@login_required
def misc(request):
    if 'action' in request.GET:
        action = request.GET['action']
        if action == 'markread':
            user = request.user
            PostTracking.objects.filter(user__id=user.id).update(last_read=timezone.now(), topics=None)
            messages.info(request, _("Marked all topics as read."))
            return HttpResponseRedirect(reverse('djangobb:index'))

        elif action == 'report':
            if request.GET.get('post_id', ''):
                post_id = request.GET['post_id']
                post = get_object_or_404(Post, id=post_id)
                form = build_form(ReportForm, request, reported_by=request.user, post=post_id)
                if request.method == 'POST' and form.is_valid():
                    form.save()
                    messages.info(request, _("Post reported."))
                    return HttpResponseRedirect(post.get_absolute_url())
                return render(request, 'djangobb_forum/report.html', {
                    'form': form,
                    'post': post,
                    })

    elif 'submit' in request.POST and 'mail_to' in request.GET:
        form = MailToForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=request.GET['mail_to'])
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body'] + u'\n %s %s [%s]' % (Site.objects.get_current().domain,
                                                                  request.user.username,
                                                                  request.user.email)
            try:
                user.email_user(subject, body, request.user.email)
                messages.success(request, _("Email sent."))
            except Exception:
                messages.error(request, _("Email could not be sent."))
            return HttpResponseRedirect(reverse('djangobb:index'))

    elif 'mail_to' in request.GET:
        mailto = get_object_or_404(User, username=request.GET['mail_to'])
        form = MailToForm()
        return render(request, 'djangobb_forum/mail_to.html', {'form':form,
                'mailto': mailto}
                )


def show_forum(request, forum_id, full=True):
    forum = get_object_or_404(Forum, pk=forum_id)
    if not forum.category.has_access(request.user):
        return HttpResponseForbidden()
    topics = forum.topics.order_by('-sticky', '-updated').select_related('last_post__user', 'user')
    moderator = request.user.is_superuser or\
        request.user in forum.moderators.all()
    to_return = {'categories': Category.objects.all(),
                'forum': forum,
                'posts': forum.post_count,
                'topics': topics,
                'moderator': moderator,
                'can_create_topics': (not forum.moderator_only or request.user.is_superuser or request.user in forum.moderators.all()) and request.user.is_authenticated,
                }
    if full:
        return render(request, 'djangobb_forum/forum.html', to_return)
    else:
        return render(request, 'djangobb_forum/mobile/forum.html', to_return)


@transaction.commit_on_success
def show_topic(request, topic_id, full=True):
    """
    * Display a topic
    * save a reply
    * save a poll vote
    """
    post_request = request.method == "POST"
    user_is_authenticated = request.user.is_authenticated()
    if post_request and not user_is_authenticated:
        # Info: only user that are logged in should get forms in the page.
        return HttpResponseForbidden()

    topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
    if not topic.forum.category.has_access(request.user):
        return HttpResponseForbidden()
    Topic.objects.filter(pk=topic.id).update(views=F('views') + 1)
    last_post = topic.last_post

    if request.user.is_authenticated():
        topic.update_read(request.user)
    # without specifying, following query wouldn't select related properly
    posts = topic.posts.select_related('user__userprofile',
        'user__forum_profile',
        'updated_by', 'user').prefetch_related('user__groups').all()
    edit_start = timezone.now() - timedelta(minutes=1)
    edit_end = timezone.now()
    editable = posts.filter(created__range=(edit_start, edit_end)).filter(user_id=request.user.id)
    can_edit = request.user.has_perm('djangobb_forum.change_post')
    try:
        page_url_parameter = int(request.GET.get('page') or 1)
    except:
        page_url_parameter = 1
    first_post_number = int(forum_settings.TOPIC_PAGE_SIZE) * (page_url_parameter - 1)
    can_close = can_close_topic(request.user, topic)

    moderator = request.user.is_superuser or request.user in topic.forum.moderators.all()
    if user_is_authenticated and request.user in topic.subscribers.all():
        subscribed = True
    else:
        subscribed = False

    # reply form
    reply_form = None
    form_url = None
    back_url = None
    if user_is_authenticated and (not topic.closed or moderator):
        form_url = request.path + '?' + request.META['QUERY_STRING'] + '#reply' # if form validation failed: browser should scroll down to reply form ;)
        back_url = request.path
        ip = get_client_ip(request)
        post_form_kwargs = {
            "topic":topic,
            "user":request.user,
            "request_data":request.META,
            "ip":ip,
            'is_ip_banned': request.is_ip_banned,
        }
        if post_request and AddPostForm.FORM_NAME in request.POST:

            reply_form = AddPostForm(request.POST, request.FILES, **post_form_kwargs)
            if reply_form.is_valid():
                post = reply_form.save()
                messages.success(request, _("Reply saved."))
                return HttpResponseRedirect(post.get_absolute_url() if full else post.get_mobile_url())
        else:
            reply_form = AddPostForm(
                initial={
                    'markup': request.user.forum_profile.markup,
                    'subscribe': False,
                },
                **post_form_kwargs
            )

    group_titles = {}
    
    for post in posts:
        
        if post.user.is_superuser:
            group_titles[post.user] = "Scratch Team"
            
        else: 
            temp_names = [group.name for group in post.user.groups.all()]
            if "Forum Moderators" in temp_names:
                group_titles[post.user] = "Forum Moderator"
            elif "Scratchers" in temp_names:
                group_titles[post.user] = "Scratcher"
            elif "New Scratchers" in temp_names:
                group_titles[post.user] = "New to Scratch"
            else:
                group_titles[post.user] = "Ungrouped"
    
        
    # handle poll, if exists
    poll_form = None
    polls = topic.poll_set.all()
    if not polls:
        poll = None
    else:
        poll = polls[0]
        if user_is_authenticated: # Only logged in users can vote
            poll.auto_deactivate()
            has_voted = request.user in poll.users.all()
            if not post_request or not VotePollForm.FORM_NAME in request.POST:
                # It's not a POST request or: The reply form was send and not a poll vote
                if poll.active and not has_voted:
                    poll_form = VotePollForm(poll)
            else:
                if not poll.active:
                    messages.error(request, _("This poll is not active."))
                    return HttpResponseRedirect(topic.get_absolute_url())
                elif has_voted:
                    messages.error(request, _("You already voted on this poll."))
                    return HttpResponseRedirect(topic.get_absolute_url())

                poll_form = VotePollForm(poll, request.POST)
                if poll_form.is_valid():
                    ids = poll_form.cleaned_data["choice"]
                    queryset = poll.choices.filter(id__in=ids)
                    queryset.update(votes=F('votes') + 1)
                    poll.users.add(request.user) # save that this user has vote
                    messages.success(request, _("Vote saved."))
                    return HttpResponseRedirect(topic.get_absolute_url())

    highlight_word = request.GET.get('hl', '')
    if full:
        return render(request, 'djangobb_forum/topic.html', {'categories': Category.objects.all(),
                'topic': topic,
                'last_post': last_post,
                'form_url': form_url,
                'reply_form': reply_form,
                'back_url': back_url,
                'moderator': moderator,
                'subscribed': subscribed,
                'posts': posts,
                'first_post_number': first_post_number,
                'highlight_word': highlight_word,
                'poll': poll,
                'poll_form': poll_form,
                'editable': editable,
                'can_edit': can_edit,
                'can_close': can_close,
                'group_titles': group_titles,
                'simple_user_agent': simple_user_agent(request),
                })
    else:
        return render(request, 'djangobb_forum/mobile/topic.html', {'categories': Category.objects.all(),
                'topic': topic,
                'posts': posts,
                'poll': poll,
                'poll_form': poll_form,
                'reply_form': reply_form,
                })

def show_unread_posts(request, topic_id, full=True):
    post = None
    user = request.user
    topic = get_object_or_404(Topic, pk=topic_id)
    if user.posttracking is not None:
        topics = user.posttracking.topics;
        if isinstance(topics, dict):
            pk = topics.get(str(topic_id), 0)
            try:
                post = Post.objects.filter(topic=topic, pk__gt=pk).order_by('pk')[0]
            except IndexError:
                pass
        else:
            last_read = user.posttracking.last_read
            if last_read is not None:
                posts = Post.objects.filter(Q(topic=topic) & (Q(created__gte=last_read) | Q(updated__gte=last_read))).order_by('pk')
                try:
                    post = posts[0]
                except Post.DoesNotExist:
                    pass
    if post is None:
        post = topic.last_post

    return redirect(post.get_absolute_url() if full else post.get_mobile_url());

@login_required
@transaction.commit_on_success
def add_topic(request, forum_id, full=True):
    """
    create a new topic, with or without poll
    """
    forum = get_object_or_404(Forum, pk=forum_id)
    if not forum.category.has_access(request.user) or (forum.moderator_only and not (request.user.is_superuser or request.user in forum.moderators.all())):
        return HttpResponseForbidden()

    ip = get_client_ip(request)
    post_form_kwargs = {
        "forum": forum,
        "user": request.user,
        "request_data":request.META,
        "ip": ip,
        "is_ip_banned": request.is_ip_banned,
    }

    if request.method == 'POST':
        form = AddPostForm(request.POST, request.FILES, **post_form_kwargs)
        if form.is_valid():
            all_valid = True
        else:
            all_valid = False

        poll_form = PollForm(request.POST)
        create_poll = poll_form.create_poll()
        if not create_poll:
            # All poll fields are empty: User didn't want to create a poll
            # Don't run validation and remove all form error messages
            poll_form = PollForm() # create clean form without form errors
        elif not poll_form.is_valid():
            all_valid = False

        if all_valid:
            post = form.save()
            if create_poll:
                poll_form.save(post)
                messages.success(request, _("Topic with poll saved."))
            else:
                messages.success(request, _("Topic saved."))
            return HttpResponseRedirect(post.get_absolute_url() if full else post.get_mobile_url())
    else:
        form = AddPostForm(
            initial={
                'markup': request.user.forum_profile.markup,
                'subscribe': True,
            },
            **post_form_kwargs
        )

    # if creating a new topic and allowed
    create_poll_form = forum_id and forum_settings.ALLOW_POLLS

    poll_form = PollForm()

    context = {
        'forum': forum,
        'create_poll_form': create_poll_form,
        'poll_form': poll_form,
        'form': form,
        'form_url': request.path,
        'back_url': forum.get_absolute_url(),
        'simple_user_agent': simple_user_agent(request),
    }
    return render(request, 'djangobb_forum/add_topic.html' if full else 'djangobb_forum/mobile/add_topic.html', context)


@transaction.commit_on_success
def upload_avatar(request, username, template=None, form_class=None):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and user == request.user or request.user.is_superuser:
        form = build_form(form_class, request, instance=user.forum_profile)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, _("Avatar uploaded."))
            return HttpResponseRedirect(reverse('djangobb:forum_settings', args=[user.username]))
        return render(request, template, {'form': form,
                'avatar_width': forum_settings.AVATAR_WIDTH,
                'avatar_height': forum_settings.AVATAR_HEIGHT,
               })
    else:
        topic_count = Topic.objects.filter(user__id=user.id).count()
        if user.forum_profile.post_count < forum_settings.POST_USER_SEARCH and not request.user.is_authenticated():
            messages.error(request, _("Please sign in."))
            return HttpResponseRedirect(reverse('user_signin') + '?next=%s' % request.path)
        return render(request, template, {'profile': user,
                'topic_count': topic_count,
               })


@transaction.commit_on_success
def settings(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and (user == request.user or request.user.is_staff or request.user.has_perm('djangobb_forum.change_report')):
        form = build_form(PersonalityProfileForm, request, instance=user.forum_profile, extra_args={'request': request})
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, _("Profile saved."))
        return render(request, 'djangobb_forum/profile/profile_personality.html', {
            'profile': user,
            'form': form,
        })
    # anyone else
    raise Http404

@login_required
@transaction.commit_on_success
def reputation(request, username):
    user = get_object_or_404(User, username=username)
    form = build_form(ReputationForm, request, from_user=request.user, to_user=user)

    if 'action' in request.GET:
        if request.user == user:
            return HttpResponseForbidden(u'You can not change the reputation of yourself')

        if 'post_id' in request.GET:
            post_id = request.GET['post_id']
            form.fields['post'].initial = post_id
            if request.GET['action'] == 'plus':
                form.fields['sign'].initial = 1
            elif request.GET['action'] == 'minus':
                form.fields['sign'].initial = -1
            return render(request, 'djangobb_forum/reputation_form.html', {'form': form})
        else:
            raise Http404

    elif request.method == 'POST':
        if 'del_reputation' in request.POST and request.user.is_superuser:
            reputation_list = request.POST.getlist('reputation_id')
            for reputation_id in reputation_list:
                reputation = get_object_or_404(Reputation, pk=reputation_id)
                reputation.delete()
            messages.success(request, _("Reputation deleted."))
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif form.is_valid():
            form.save()
            post_id = request.POST['post']
            post = get_object_or_404(Post, id=post_id)
            messages.success(request, _("Reputation saved."))
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            return render(request, 'djangobb_forum/reputation_form.html', {'form': form})
    else:
        reputations = Reputation.objects.filter(to_user__id=user.id).order_by('-time').select_related()
        return render(request, 'djangobb_forum/reputation.html', {'reputations': reputations,
                'profile': user.forum_profile,
               })


def show_post(request, post_id, full=True):
    post = get_object_or_404(Post, pk=post_id)
    count = post.topic.posts.filter(created__lt=post.created).count() + 1
    page = math.ceil(count / float(forum_settings.TOPIC_PAGE_SIZE))
    url = '%s?page=%d#post-%d' % (reverse('djangobb:topic' if full else 'djangobb:mobile_topic', args=[post.topic.id]), page, post.id)
    return HttpResponseRedirect(url)

@csrf_exempt
def get_post_source(request, post_id):
    """
    Raw (plain text) post source for quoting
    """
    post = get_object_or_404(Post, pk=post_id)
    return HttpResponse(post.body, mimetype='text/plain')

@csrf_exempt
def get_topic_title(request, topic_id):
    """
    Raw (plain text) topic title for move posts confirmation
    """
    topic = get_object_or_404(Topic, pk=topic_id)
    return HttpResponse(topic.name, mimetype='text/plain')

@login_required
@transaction.commit_on_success
def edit_post(request, post_id):
    from djangobb_forum.templatetags.forum_extras import forum_editable_by
    post = get_object_or_404(Post, pk=post_id)
    topic = post.topic
    if not forum_editable_by(post, request.user):
        messages.error(request, _("You don't have permission to edit this post."))
        return HttpResponseRedirect(post.get_absolute_url())
    moderator = request.user.is_superuser or request.user in topic.forum.moderators.all()
    form = build_form(EditPostForm, request, topic=topic, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        if not form.cleaned_data['silent_edit']:
            post.updated_by = request.user
            post.updated = timezone.now()
        post.save()
        messages.success(request, _("Post updated."))
        return HttpResponseRedirect(post.get_absolute_url())

    return render(request, 'djangobb_forum/edit_post.html', {'form': form,
            'post': post,
            'moderator': moderator,
            })


@login_required
@transaction.commit_on_success
def delete_posts(request, topic_id):

    topic = Topic.objects.select_related().get(pk=topic_id)

    if forum_moderated_by(topic, request.user):
        deleted = False
        post_list = request.POST.getlist('post')
        for post_id in post_list:
            if not deleted:
                deleted = True
            delete_post(request, post_id)
        if deleted:
            messages.success(request, _("Post deleted."))
            return HttpResponseRedirect(topic.get_absolute_url())

    last_post = topic.posts.latest()

    if request.user.is_authenticated():
        topic.update_read(request.user)

    posts = topic.posts.all().select_related()

    initial = {}
    if request.user.is_authenticated():
        initial = {'markup': request.user.forum_profile.markup}
    form = AddPostForm(topic=topic, initial=initial, is_ip_banned=request.is_ip_banned)

    moderator = request.user.is_superuser or\
        request.user in topic.forum.moderators.all()
    if request.user.is_authenticated() and request.user in topic.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    return render(request, 'djangobb_forum/delete_posts.html', {
            'topic': topic,
            'last_post': last_post,
            'form': form,
            'moderator': moderator,
            'subscribed': subscribed,
            'posts': posts,
            })


@login_required
@transaction.commit_on_success
def move_posts(request, topic_id):

    topic = Topic.objects.select_related().get(pk=topic_id)
    from_forum = topic.forum

    if forum_moderated_by(topic, request.user):
        moved = False
        post_list = request.POST.getlist('post')
        if 'to_topic' in request.POST:
            match = re.match(r'.*?(\d+)', request.POST['to_topic'])
            if match is None:
                messages.error(request, _("The topic ID must be an integer."))
            else:
                to_topic_id = int(match.group(1))
                try:
                    to_topic = Topic.objects.select_related().get(pk=to_topic_id)
                except Topic.DoesNotExist:
                    messages.error(request, _("That thread doesn't exist."))
                else:
                    if 'move_all' in request.POST:
                        Post.objects.filter(topic=topic).update(topic=to_topic)
                        topic.delete()
                        moved = True
                        deleted = True
                    else:
                        for post_id in post_list:
                            if not moved:
                                moved = True
                            post = get_object_or_404(Post, pk=post_id)
                            if post.topic != to_topic:
                                last = (topic.last_post == post)
                                if forum_moderated_by(to_topic, request.user):
                                    post.topic = to_topic
                                    post.save()
                        if Post.objects.filter(topic__id=topic.id).count() == 0:
                            topic.delete()
                            deleted = True
                        else:
                            deleted = False
                            try:
                                topic.last_post = Post.objects.filter(topic__id=topic.id).latest()
                            except Post.DoesNotExist:
                                topic.last_post = None
                            topic.post_count = Post.objects.filter(topic__id=topic.id).count()
                            topic.save()
                    try:
                        from_forum.last_post = Post.objects.filter(topic__forum__id=from_forum.id).latest()
                    except Post.DoesNotExist:
                        from_forum.last_post = None
                    from_forum.post_count = Post.objects.filter(topic__forum__id=from_forum.id).count()
                    from_forum.topic_count = Topic.objects.filter(forum__id=from_forum.id).count()
                    from_forum.save()

                    to_topic.post_count = Post.objects.filter(topic__id=to_topic.id).count()
                    to_topic.save()


                    if moved:
                        messages.success(request, _("Posts moved."))
                        if not deleted:
                            return HttpResponseRedirect(topic.get_absolute_url())
                        else:
                            return HttpResponseRedirect(from_forum.get_absolute_url())

    last_post = topic.posts.latest()

    if request.user.is_authenticated():
        topic.update_read(request.user)

    posts = topic.posts.all().select_related()

    initial = {}
    if request.user.is_authenticated():
        initial = {'markup': request.user.forum_profile.markup}
    form = AddPostForm(topic=topic, initial=initial, is_ip_banned=request.is_ip_banned)

    moderator = request.user.is_superuser or\
        request.user in topic.forum.moderators.all()
    if request.user.is_authenticated() and request.user in topic.subscribers.all():
        subscribed = True
    else:
        subscribed = False
    return render(request, 'djangobb_forum/move_posts.html', {'categories': Category.objects.all(),
            'exclude_topic': from_forum,
            'topic': topic,
            'last_post': last_post,
            'form': form,
            'moderator': moderator,
            'subscribed': subscribed,
            'posts': posts,
            })

@login_required
@transaction.commit_on_success
def move_topic(request):
    if 'topic_id' in request.GET:
        #if move only 1 topic
        topic_ids = [request.GET['topic_id']]
    else:
        topic_ids = request.POST.getlist('topic_id')
    first_topic = topic_ids[0]
    topic = get_object_or_404(Topic, pk=first_topic)
    from_forum = topic.forum
    if 'to_forum' in request.POST:
        to_forum_id = int(request.POST['to_forum'])
        to_forum = get_object_or_404(Forum, pk=to_forum_id)
        for topic_id in topic_ids:
            topic = get_object_or_404(Topic, pk=topic_id)
            if topic.forum != to_forum:
                if forum_moderated_by(topic, request.user):
                    topic.forum = to_forum
                    topic.save()

        #TODO: not DRY
        try:
            last_post = Post.objects.filter(topic__forum__id=from_forum.id).latest()
        except Post.DoesNotExist:
            last_post = None
        from_forum.last_post = last_post
        from_forum.topic_count = from_forum.topics.count()
        from_forum.post_count = from_forum.posts.count()
        from_forum.save()
        messages.success(request, _("Topic moved."))
        return HttpResponseRedirect(to_forum.get_absolute_url())

    return render(request, 'djangobb_forum/move_topic.html', {'categories': Category.objects.all(),
            'topic_ids': topic_ids,
            'exclude_forum': from_forum,
            })


@login_required
@transaction.commit_on_success
def stick_unstick_topic(request, topic_id, action):
    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if action == 's':
            topic.sticky = True
            messages.success(request, _("Topic stickied."))
        elif action == 'u':
            messages.success(request, _("Topic unstickied."))
            topic.sticky = False
        topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
@transaction.commit_on_success
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    last_post = post.topic.last_post
    topic = post.topic
    forum = post.topic.forum
    is_head = topic.posts.order_by('created')[0].id == post.id

    if not (request.user.is_superuser or\
        request.user in post.topic.forum.moderators.all() or \
        (post.user == request.user and post == last_post)):
        messages.success(request, _("You don't have permission to delete this post."))
        return HttpResponseRedirect(post.get_absolute_url())
    delete_kwargs = {'staff':request.user.is_superuser}
    post.delete(**delete_kwargs)
    messages.success(request, _("Post deleted."))

    if is_head:
        return HttpResponseRedirect(forum.get_absolute_url())
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
@transaction.commit_on_success
def open_close_topic(request, topic_id, action):
    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user) or can_close_topic(request.user, topic):
        if action == 'c':
            topic.closed = True
            messages.success(request, _("Topic closed."))
        elif action == 'o':
            topic.closed = False
            messages.success(request, _("Topic opened."))
        topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def users(request):
    if not (request.user.is_superuser):
            raise Http404
    users = User.objects.filter(forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('username')
    form = UserSearchForm(request.GET)
    users = form.filter(users)
    return render(request, 'djangobb_forum/users.html', {'users': users,
            'form': form,
            })


@login_required
@transaction.commit_on_success
def delete_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.remove(request.user)
    messages.info(request, _("Unsubscribed from topic."))
    if 'from_topic' in request.GET:
        return HttpResponseRedirect(reverse('djangobb:topic', args=[topic.id]))
    else:
        return HttpResponseRedirect(reverse('djangobb:forum_settings', args=[request.user.username]))


@login_required
@transaction.commit_on_success
def add_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.add(request.user)
    messages.success(request, _("Subscribed to topic."))
    return HttpResponseRedirect(reverse('djangobb:topic', args=[topic.id]))


@login_required
def show_attachment(request, hash):
    attachment = get_object_or_404(Attachment, hash=hash)
    file_data = file(attachment.get_absolute_path(), 'rb').read()
    response = HttpResponse(file_data, mimetype=attachment.content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % smart_str(attachment.name)
    return response


@login_required
@csrf_exempt
def post_preview(request):
    '''Preview for markitup'''
    data = request.POST.get('data', '')

    try:
        data = convert_text_to_html(data, request.user.forum_profile)
    except UnapprovedImageError as e:
        return render(request, 'djangobb_forum/post_preview.html', {
            'data': e.user_error()
        })
    if forum_settings.SMILES_SUPPORT:
        data = smiles(data)
    return render(request, 'djangobb_forum/post_preview.html', {'data': data})

def show_youtube_video(request, video_id):
    try:
        response = urllib2.urlopen('http://gdata.youtube.com/feeds/api/videos/%s?v=2' % video_id)
    except urllib2.HTTPError:
        title = None
    else:
        try:
            start_tag = '<media:title type=\'plain\'>'
            end_tag = '</media:title>'
            atom = response.read()
            start = atom.index(start_tag) + len(start_tag)
            end = atom.index(end_tag)
            title = atom[start:end]
        except ValueError:
            title = None

    return render(request, 'djangobb_forum/youtube.html', {
        'video_id': video_id,
        'video_title': title,
        })

@login_required
def mobile_reply(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not request.user.is_authenticated or post.topic.closed and not (request.user.is_superuser or request.user in forum.moderators.all()):
        raise Http404
    ip = get_client_ip(request)
    post_form_kwargs = {
        "topic":post.topic,
        "user":request.user,
        "request_data":request.META,
        "ip":ip,
        'is_ip_banned': request.is_ip_banned,
    }
    if AddPostForm.FORM_NAME in request.POST:
        reply_form = AddPostForm(request.POST, request.FILES, **post_form_kwargs)
        if reply_form.is_valid():
            post = reply_form.save()
            messages.success(request, _("Reply saved."))
            return HttpResponseRedirect(post.get_mobile_url())
    else:
        reply_form = AddPostForm(
            initial={
                'markup': request.user.forum_profile.markup,
                'subscribe': False,
                'body':'[quote=' + post.user.username + ']' + post.body + '[/quote]\n',
            },
            **post_form_kwargs
        )
    return render(request, 'djangobb_forum/mobile/reply.html', {
        'form': reply_form,
        'post': post
        })

def get_user_post_count(request, username):
    if not forum_extras.forum_can_view_reports(request.user):
        raise Http404
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse('', mimetype='text/plain')
    return HttpResponse(str(Post.objects.filter(~Q(topic__forum__id = forum_settings.SOFT_DELETE_TOPICS), user=user).count()), mimetype='text/plain')

def delete_all_posts_by_user(request, username):
    if not forum_extras.forum_can_view_reports(request.user):
        raise Http404
    try:
        user = User.objects.get(username=username)
        for p in Post.objects.filter(~Q(topic__forum__id = forum_settings.SOFT_DELETE_TOPICS), user=user)[:20]:
            p.delete()
    except User.DoesNotExist:
        pass
    return HttpResponse('')
