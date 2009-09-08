from django.conf.urls.defaults import *

from forum import settings as forum_settings
from forum import views as forum_views
from openauth import views as openauth_views

urlpatterns = patterns('',

    # Forum
    url('^$', forum_views.index, name='index'),
    url('^(?P<forum_id>\d+)/$', forum_views.show_forum, name='forum'),
    url('^moderate/(?P<forum_id>\d+)/$', forum_views.moderate, name='moderate'),
    url('^search/$', forum_views.search, name='search'),
    url('^misc/$', forum_views.misc, name='misc'),

        # Account
    ('account/', include('django_authopenid.urls')),

    # User
    url('^user/(?P<username>.*)/$', forum_views.user, name='forum_profile'),
    url('^users/$', forum_views.users, name='forum_users'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', forum_views.show_topic, name='topic'),
    url('^(?P<forum_id>\d+)/topic/add/$', forum_views.add_post,
        {'topic_id': None}, name='add_topic'),
    url('^topic/(?P<topic_id>\d+)/delete_posts/$', forum_views.delete_posts, name='delete_posts'),
    url('^topic/(?P<topic_id>\d+)/move/$', forum_views.move_topic, name='move_topic'),
    url('^topic/(?P<topic_id>\d+)/stick/$', forum_views.stick_topic, name='stick_topic'),
    url('^topic/(?P<topic_id>\d+)/unstick/$', forum_views.unstick_topic, name='unstick_topic'),
    url('^topic/(?P<topic_id>\d+)/close/$', forum_views.close_topic, name='close_topic'),
    url('^topic/(?P<topic_id>\d+)/open/$', forum_views.open_topic, name='open_topic'),

    # Post
    url('^topic/(?P<topic_id>\d+)/post/add/$', forum_views.add_post,
        {'forum_id': None}, name='add_post'),
    url('^post/(?P<post_id>\d+)/$', forum_views.show_post, name='post'),
    url('^post/(?P<post_id>\d+)/edit/$', forum_views.edit_post, name='edit_post'),
    url('^post/(?P<post_id>\d+)/delete/$', forum_views.delete_post, name='delete_post'),
    # Post preview
    url(r'^preview/$', forum_views.post_preview),

    # Subscription
    url('^subscription/topic/(?P<topic_id>\d+)/delete/$', forum_views.delete_subscription, name='forum_delete_subscription'),
    url('^subscription/topic/(?P<topic_id>\d+)/add/$', forum_views.add_subscription, name='forum_add_subscription'),
)


### EXTENSIONS ###

# LOFI Extension
if (forum_settings.LOFI_SUPPORT):
    urlpatterns += patterns('',
        url('^lofi/$', forum_views.index, {'full':False}, name='lofi_index'),
        url('^(?P<forum_id>\d+)/lofi/$', forum_views.show_forum, {'full':False}, name='lofi_forum'),
        url('^topic/(?P<topic_id>\d+)/lofi/$', forum_views.show_topic, {'full':False}, name='lofi_topic'),
    )

# PM Extension
if (forum_settings.PM_SUPPORT):
    urlpatterns += patterns('',
        url('^pm/new/$', forum_views.create_pm, name='forum_create_pm'),
        url('^pm/outbox/$', forum_views.pm_outbox, name='forum_pm_outbox'),
        url('^pm/inbox/$', forum_views.pm_inbox, name='forum_pm_inbox'),
        url('^pm/show/(?P<pm_id>\d+)/$', forum_views.show_pm, name='forum_show_pm'),
   )

# REPUTATION Extension
if (forum_settings.REPUTATION_SUPPORT):
    urlpatterns += patterns('',
        url('^reputation/(?P<username>.*)/$', forum_views.reputation, name='reputation'),
    )

# ATTACHMENT Extension
if (forum_settings.ATTACHMENT_SUPPORT):
    urlpatterns += patterns('',
        url('^attachment/(?P<hash>\w+)/$', forum_views.show_attachment, name='forum_attachment'),
    )