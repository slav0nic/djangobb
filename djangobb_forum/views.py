import math
from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404, render
from django.http import Http404, HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.db.models import Q, F, Sum
from django.utils.encoding import smart_str
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from djangobb_forum import settings as forum_settings
from djangobb_forum.forms import AddPostForm, EditPostForm, UserSearchForm, \
    PostSearchForm, ReputationForm, MailToForm, EssentialsProfileForm, \
    PersonalProfileForm, MessagingProfileForm, PersonalityProfileForm, \
    DisplayProfileForm, PrivacyProfileForm, ReportForm, UploadAvatarForm
from djangobb_forum.models import Category, Forum, Topic, Post, Profile, Reputation, \
    Attachment, PostTracking
from djangobb_forum.templatetags import forum_extras
from djangobb_forum.templatetags.forum_extras import forum_moderated_by
from djangobb_forum.util import build_form, paginate, set_language, smiles, convert_text_to_html

from haystack.query import SearchQuerySet, SQ
from django.contrib import messages
from django.core.exceptions import SuspiciousOperation


def index(request, full=True):
    users_cached = cache.get('djangobb_users_online', {})
    users_online = users_cached and User.objects.filter(id__in=users_cached.keys()) or []
    guests_cached = cache.get('djangobb_guests_online', {})
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
            {'id': forum.category.id, 'cat': forum.category, 'forums': []})
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
        return render(request, 'djangobb_forum/index.html', to_return)
    else:
        return render(request, 'djangobb_forum/lofi/index.html', to_return)


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
            messages.success(request, _("Topics deleted"))
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif 'open_topics' in request.POST:
            for topic_id in topic_ids:
                open_close_topic(request, topic_id, 'o')
            messages.success(request, _("Topics opened"))
            return HttpResponseRedirect(reverse('djangobb:index'))
        elif 'close_topics' in request.POST:
            for topic_id in topic_ids:
                open_close_topic(request, topic_id, 'c')
            messages.success(request, _("Topics closed"))
            return HttpResponseRedirect(reverse('djangobb:index'))

        return render(request, 'djangobb_forum/moderate.html', {'forum': forum,
                'topics': topics,
                #'sticky_topics': forum.topics.filter(sticky=True),
                'posts': forum.posts.count(),
                })
    else:
        raise Http404


def search(request):
    # TODO: used forms in every search type

    def _render_search_form(form=None):
        return render(request, 'djangobb_forum/search_form.html', {'categories': Category.objects.all(),
                'form': form,
                })

    if not 'action' in request.GET:
        return _render_search_form(form=PostSearchForm())

    if request.GET.get("show_as") == "posts":
        show_as_posts = True
        template_name = 'djangobb_forum/search_posts.html'
    else:
        show_as_posts = False
        template_name = 'djangobb_forum/search_topics.html'

    context = {}

    #FIXME: show_user for anonymous raise exception, 
    #django bug http://code.djangoproject.com/changeset/14087 :|
    groups = request.user.groups.all() or [] #removed after django > 1.2.3 release
    topics = Topic.objects.filter(
               Q(forum__category__groups__in=groups) | \
               Q(forum__category__groups__isnull=True))

    base_url = None
    _generic_context = True

    action = request.GET['action']
    if action == 'show_24h':
        date = datetime.today() - timedelta(1)
        topics = topics.filter(created__gte=date)
    elif action == 'show_new':
        try:
            last_read = PostTracking.objects.get(user=request.user).last_read
        except PostTracking.DoesNotExist:
            last_read = None
        if last_read:
            topics = topics.filter(last_post__updated__gte=last_read).all()
        else:
            #searching more than forum_settings.SEARCH_PAGE_SIZE in this way - not good idea :]
            topics = [topic for topic in topics[:forum_settings.SEARCH_PAGE_SIZE] if forum_extras.has_unreads(topic, request.user)]

    elif action == 'show_unanswered':
        topics = topics.filter(post_count=1)
    elif action == 'show_subscriptions':
        topics = topics.filter(subscribers__id=request.user.id)
    elif action == 'show_user':
        # Show all posts from user or topics started by user
        user_id = request.GET.get("user_id", request.user.id)
        user_id = int(user_id)
        posts = Post.objects.filter(user__id=user_id)
        base_url = "?action=show_user&user_id=%s&show_as=" % user_id
        if not show_as_posts:
            # show as topic
            # FIXME: This should be speed up. This is not lazy:
            user_topics = []
            for post in posts:
                topic = post.topic
                if topic in topics and topic not in user_topics:
                    user_topics.append(topic)
            topics = user_topics
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

        # add exlusions for categories user does not have access too
        for category in Category.objects.all():
            if not category.has_access(request.user):
                query = query.exclude(category=category)

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
            context["topics"] = Topic.objects.filter(posts__in=post_pks).distinct()
        else:
            context["posts"] = posts

        get_query_dict = request.GET.copy()
        get_query_dict.pop("show_as")
        base_url = "?%s&show_as=" % get_query_dict.urlencode()
        _generic_context = False

    if _generic_context:
        if show_as_posts:
            context["posts"] = Post.objects.filter(topic__in=topics).order_by('-created')
        else:
            context["topics"] = topics

    if base_url is None:
        base_url = "?action=%s&show_as=" % action

    if show_as_posts:
        context["as_topic_url"] = base_url + "topics"
    else:
        context["as_post_url"] = base_url + "posts"

    return render(request, template_name, context)




@login_required
def misc(request):
    if 'action' in request.GET:
        action = request.GET['action']
        if action == 'markread':
            user = request.user
            PostTracking.objects.filter(user__id=user.id).update(last_read=datetime.now(), topics=None)
            messages.info(request, _("All topics marked as read."))
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
                return render(request, 'djangobb_forum/report.html', {'form':form})

    elif 'submit' in request.POST and 'mail_to' in request.GET:
        form = MailToForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, username=request.GET['mail_to'])
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body'] + '\n %s %s [%s]' % (Site.objects.get_current().domain,
                                                                  request.user.username,
                                                                  request.user.email)
            user.email_user(subject, body, request.user.email)
            messages.success(request, _("Email send."))
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
    topics = forum.topics.order_by('-sticky', '-updated').select_related()
    moderator = request.user.is_superuser or\
        request.user in forum.moderators.all()
    to_return = {'categories': Category.objects.all(),
                'forum': forum,
                'posts': forum.post_count,
                'topics': topics,
                'moderator': moderator,
                }
    if full:
        return render(request, 'djangobb_forum/forum.html', to_return)
    else:
        return render(request, 'djangobb_forum/lofi/forum.html', to_return)


@transaction.commit_on_success
def show_topic(request, topic_id, full=True):
    topic = get_object_or_404(Topic.objects.select_related(), pk=topic_id)
    if not topic.forum.category.has_access(request.user):
        return HttpResponseForbidden()
    Topic.objects.filter(pk=topic.id).update(views=F('views') + 1)

    last_post = topic.last_post

    if request.user.is_authenticated():
        topic.update_read(request.user)
    posts = topic.posts.all().select_related()

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
        return render(request, 'djangobb_forum/topic.html', {'categories': Category.objects.all(),
                'topic': topic,
                'last_post': last_post,
                'form': form,
                'moderator': moderator,
                'subscribed': subscribed,
                'posts': posts,
                'highlight_word': highlight_word,
                })
    else:
        return render(request, 'djangobb_forum/lofi/topic.html', {'categories': Category.objects.all(),
                'topic': topic,
                'posts': posts,
                })


@login_required
@transaction.commit_on_success
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
        messages.error(request, _("This topic is closed."))
        return HttpResponseRedirect(topic.get_absolute_url())

    ip = request.META.get('REMOTE_ADDR', None)
    form = build_form(AddPostForm, request, topic=topic, forum=forum,
                      user=request.user, ip=ip,
                      initial={'markup': request.user.forum_profile.markup})

    if 'post_id' in request.GET:
        post_id = request.GET['post_id']
        post = get_object_or_404(Post, pk=post_id)
        form.fields['body'].initial = u"[quote=%s]%s[/quote]" % (post.user, post.body)

    if form.is_valid():
        post = form.save();
        messages.success(request, _("Topic saved."))
        return HttpResponseRedirect(post.get_absolute_url())

    return render(request, 'djangobb_forum/add_post.html', {'form': form,
            'posts': posts,
            'topic': topic,
            'forum': forum,
            })


@transaction.commit_on_success
def upload_avatar(request, username, template=None, form_class=None):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and user == request.user or request.user.is_superuser:
        form = build_form(form_class, request, instance=user.forum_profile)
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, _("Your avatar uploaded."))
            return HttpResponseRedirect(reverse('djangobb:forum_profile', args=[user.username]))
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
def user(request, username, section='essentials', action=None, template='djangobb_forum/profile/profile_essentials.html', form_class=EssentialsProfileForm):
    user = get_object_or_404(User, username=username)
    if request.user.is_authenticated() and user == request.user or request.user.is_superuser:
        profile_url = reverse('djangobb:forum_profile_%s' % section, args=[user.username])
        form = build_form(form_class, request, instance=user.forum_profile, extra_args={'request': request})
        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, _("User profile saved."))
            return HttpResponseRedirect(profile_url)
        return render(request, template, {'active_menu': section,
                'profile': user,
                'form': form,
               })
    else:
        template = 'djangobb_forum/user.html'
        topic_count = Topic.objects.filter(user__id=user.id).count()
        if user.forum_profile.post_count < forum_settings.POST_USER_SEARCH and not request.user.is_authenticated():
            messages.error(request, _("Please sign in."))
            return HttpResponseRedirect(reverse('user_signin') + '?next=%s' % request.path)
        return render(request, template, {'profile': user,
                'topic_count': topic_count,
               })


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


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.topic.posts.filter(created__lt=post.created).count() + 1
    page = math.ceil(count / float(forum_settings.TOPIC_PAGE_SIZE))
    url = '%s?page=%d#post-%d' % (reverse('djangobb:topic', args=[post.topic.id]), page, post.id)
    return HttpResponseRedirect(url)


@login_required
@transaction.commit_on_success
def edit_post(request, post_id):
    from djangobb_forum.templatetags.forum_extras import forum_editable_by

    post = get_object_or_404(Post, pk=post_id)
    topic = post.topic
    if not forum_editable_by(post, request.user):
        messages.error(request, _("No permissions to edit this post."))
        return HttpResponseRedirect(post.get_absolute_url())
    form = build_form(EditPostForm, request, topic=topic, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.updated_by = request.user
        post.save()
        messages.success(request, _("Post updated."))
        return HttpResponseRedirect(post.get_absolute_url())

    return render(request, 'djangobb_forum/edit_post.html', {'form': form,
            'post': post,
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
    form = AddPostForm(topic=topic, initial=initial)

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
            messages.success(request, _("Topic marked as sticky."))
        elif action == 'u':
            messages.success(request, _("Sticky flag removed from topic."))
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

    if not (request.user.is_superuser or\
        request.user in post.topic.forum.moderators.all() or \
        (post.user == request.user and post == last_post)):
        messages.success(request, _("You haven't the permission to delete this post."))
        return HttpResponseRedirect(post.get_absolute_url())

    post.delete()
    messages.success(request, _("Post deleted."))

    try:
        Topic.objects.get(pk=topic.id)
    except Topic.DoesNotExist:
        #removed latest post in topic
        return HttpResponseRedirect(forum.get_absolute_url())
    else:
        return HttpResponseRedirect(topic.get_absolute_url())


@login_required
@transaction.commit_on_success
def open_close_topic(request, topic_id, action):
    topic = get_object_or_404(Topic, pk=topic_id)
    if forum_moderated_by(topic, request.user):
        if action == 'c':
            topic.closed = True
            messages.success(request, _("Topic closed."))
        elif action == 'o':
            topic.closed = False
            messages.success(request, _("Topic opened."))
        topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


def users(request):
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
    messages.info(request, _("Topic subscription removed."))
    if 'from_topic' in request.GET:
        return HttpResponseRedirect(reverse('djangobb:topic', args=[topic.id]))
    else:
        return HttpResponseRedirect(reverse('djangobb:forum_profile', args=[request.user.username]))


@login_required
@transaction.commit_on_success
def add_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.add(request.user)
    messages.success(request, _("Topic subscribed."))
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
    markup = request.user.forum_profile.markup
    data = request.POST.get('data', '')

    data = convert_text_to_html(data, markup)
    if forum_settings.SMILES_SUPPORT:
        data = smiles(data)
    return render(request, 'djangobb_forum/post_preview.html', {'data': data})
