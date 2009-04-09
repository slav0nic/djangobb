from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from forum.models import Post, Topic, Forum, Category

class ForumFeed(Feed):
    feed_type = Atom1Feed

    def link(self):
        return reverse('forum.views.index')

    def item_guid(self, obj):
        return str(obj.id)

    def item_pubdate(self, obj):
        return obj.created

class LastPosts(ForumFeed):
    title = _('Latest posts on forum')
    description = _('Latest posts on forum')
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'

    def items(self):
        return Post.objects.order_by('-created')[:15]


class LastTopics(ForumFeed):
    title = _('Latest topics on forum')
    description = _('Latest topics on forum')
    title_template = 'forum/feeds/topics_title.html'
    description_template = 'forum/feeds/topics_description.html'

    def items(self):
        return Topic.objects.order_by('-created')[:15]
  
class LastPostsOnTopic(ForumFeed):
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'
    
    def get_object(self, topics):
        if len(topics) != 1:
            raise ObjectDoesNotExist
        return Topic.objects.get(id=topics[0])

    def title(self, obj):
        return _('Latest posts on %s topic' % obj.name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return _('Latest posts on %s topic' % obj.name)

    def items(self, obj):
       return Post.objects.filter(topic__id__exact=obj.id).order_by('-created')[:15]

    
class LastPostsOnForum(ForumFeed):
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'
    
    def get_object(self, forums):
        if len(forums) != 1:
            raise ObjectDoesNotExist
        return Forum.objects.get(id=forums[0])

    def title(self, obj):
        return _('Latest posts on %s forum' % obj.name)

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return _('Latest posts on %s forum' % obj.name)

    def items(self, obj):
       return Post.objects.filter(topic__forum__id__exact=obj.id).order_by('-created')[:15]

class LastPostsOnCategory(ForumFeed):
    title_template = 'forum/feeds/posts_title.html'
    description_template = 'forum/feeds/posts_description.html'
    
    def get_object(self, categories):
        if len(categories) != 1:
            raise ObjectDoesNotExist
        return Category.objects.get(id=categories[0])

    def title(self, obj):
        return _('Latest posts on %s category' % obj.name)

    def description(self, obj):
        return _('Latest posts on %s category' % obj.name)

    def items(self, obj):
       return Post.objects.filter(topic__forum__category__id__exact=obj.id).order_by('-created')[:15]
