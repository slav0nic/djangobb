from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings
from django.contrib import admin

from forum.feeds import LastPosts, LastTopics, LastPostsOnForum, LastPostsOnCategory, LastPostsOnTopic
from sitemap import SitemapForum, SitemapTopic
from forms import RegistrationFormUtfUsername

#Hack for add default_params with RegistrationFormUtfUsername to registration urlpattern
from django_authopenid.urls import urlpatterns as authopenid_urlpatterns
for i, rurl in enumerate(authopenid_urlpatterns):
    if rurl.name == 'registration_register':
        authopenid_urlpatterns[i].default_args = {'form_class': RegistrationFormUtfUsername}
        break

admin.autodiscover()

feeds = {
    'posts': LastPosts,
    'topics': LastTopics,
    'topic': LastPostsOnTopic,
    'forum': LastPostsOnForum,
    'category': LastPostsOnCategory,
}

sitemaps = {
    'forum': SitemapForum,
    'topic': SitemapTopic,
}

urlpatterns = patterns('',
    # Admin
    (r'^admin/', include(admin.site.urls)),
    
    # Sitemap
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    
    # Apps
    (r'^forum/account/', include(authopenid_urlpatterns)),
    (r'^forum/', include('forum.urls', namespace='djangobb')),
    
    # Feeds
    url(r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}, name='forum_feed'),
)

if (settings.DEBUG):
    urlpatterns += patterns('',
        (r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
            'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
