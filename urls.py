from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings
from django.contrib import admin
import django.views.static

from forum.feeds import LastPosts, LastTopics, LastPostsOnForum, LastPostsOnCategory, LastPostsOnTopic
from sitemap import SitemapCategory, SitemapForum, SitemapTopic


admin.autodiscover()

feeds = {
    'posts': LastPosts,
    'topics': LastTopics,
    'topic': LastPostsOnTopic,
    'forum': LastPostsOnForum,
    'category': LastPostsOnCategory,
}

sitemaps = {
    'category': SitemapCategory,
    'forum': SitemapForum,
    'topic': SitemapTopic,
}

urlpatterns = patterns('',
    # Admin
    (r'^admin/', include(admin.site.urls)),
    
    # Sitemap
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
    # Apps
    url(r'^forum/', include('apps.forum.urls')),
    
    # Feeds
    url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}, name='forum_feed'),
)

if (settings.DEBUG):
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
            django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
    )
