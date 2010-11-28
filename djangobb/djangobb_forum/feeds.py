from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404

from djangobb_forum.models import Post, Topic, Forum, Category

class ForumFeed(Feed):
    feed_type = Atom1Feed

    def link(self):
        return reverse('djangobb:index')

    def item_guid(self, obj):
        return str(obj.id)

    def item_pubdate(self, obj):
        return obj.created


class LastPosts(ForumFeed):
    title = _('Latest posts on forum')
    description = _('Latest posts on forum')
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'

    def get_object(self, request):
        user_groups = request.user.groups.all()
        if request.user.is_anonymous():
            user_groups = []
        allow_forums = Forum.objects.filter(
                Q(category__groups__in=user_groups) | \
                Q(category__groups__isnull=True))
        return allow_forums

    def items(self, allow_forums):
        return Post.objects.filter(topic__forum__in=allow_forums).order_by('-created')[:15]


class LastTopics(ForumFeed):
    title = _('Latest topics on forum')
    description = _('Latest topics on forum')
    title_template = 'forum/feeds/topics_title.html'
    description_template = 'forum/feeds/topics_description.html'

    def get_object(self, request):
        user_groups = request.user.groups.all()
        if request.user.is_anonymous():
            user_groups = []
        allow_forums = Forum.objects.filter(
                Q(category__groups__in=user_groups) | \
                Q(category__groups__isnull=True))
        return allow_forums

    def items(self, allow_forums):
        return Topic.objects.filter(forum__in=allow_forums).order_by('-created')[:15]


class LastPostsOnTopic(ForumFeed):
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'
    
    def get_object(self, request, topics):
        if len(topics) != 1:
            raise ObjectDoesNotExist
        topic = Topic.objects.get(id=topics[0])
        if not topic.forum.category.has_access(request.user):
            raise Http404
        return topic

    def title(self, obj):
        return _('Latest posts on %s topic' % obj.name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return _('Latest posts on %s topic' % obj.name)

    def items(self, obj):
        return Post.objects.filter(topic__id=obj.id).order_by('-created')[:15]


class LastPostsOnForum(ForumFeed):
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'

    def get_object(self, request, forums):
        if len(forums) != 1:
            raise ObjectDoesNotExist
        forum = Forum.objects.get(id=forums[0])
        if not forum.category.has_access(request.user):
            raise Http404
        return forum

    def title(self, obj):
        return _('Latest posts on %s forum' % obj.name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return _('Latest posts on %s forum' % obj.name)

    def items(self, obj):
        return Post.objects.filter(topic__forum__id=obj.id).order_by('-created')[:15]


class LastPostsOnCategory(ForumFeed):
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'
    
    def get_object(self, request, categories):
        if len(categories) != 1:
            raise ObjectDoesNotExist
        category = Category.objects.get(id=categories[0])
        if not category.has_access(request.user):
            raise Http404
        return category

    def title(self, obj):
        return _('Latest posts on %s category' % obj.name)

    def description(self, obj):
        return _('Latest posts on %s category' % obj.name)

    def items(self, obj):
        return Post.objects.filter(topic__forum__category__id=obj.id).order_by('-created')[:15]
