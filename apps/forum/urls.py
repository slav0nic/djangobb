from django.conf.urls.defaults import *

from apps.forum import views

urlpatterns = patterns('',
    # Account
    (r'^', include('apps.account.urls')),
    
    # Captcha
    (r'^', include('apps.captcha.urls')),
    
    # Lo-Fi version
    url('^lofi/$', views.index, {'full':False}, name='lofi_index'),
    url('^(?P<forum_id>\d+)/lofi/$', views.show_forum, {'full':False}, name='lofi_forum'),
    url('^topic/(?P<topic_id>\d+)/lofi/$', views.show_topic, {'full':False}, name='lofi_topic'),
    
    # Misc
    url('^$', views.index, name='index'),
    url('^(?P<forum_id>\d+)/$', views.show_forum, name='forum'),
    url('^moderate/(?P<forum_id>\d+)/$', views.moderate, name='moderate'),
    url('^search/$', views.search, name='search'),
    url('^misc/$', views.misc, name='misc'),
    
    # User
    url('^user/(?P<username>.*)/$', views.user, name='forum_profile'),
    url('^users/$', views.users, name='forum_users'),
    url('^reputation/(?P<username>.*)/$', views.reputation, name='reputation'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', views.show_topic, name='topic'),
    url('^(?P<forum_id>\d+)/topic/add/$', views.add_post,
        {'topic_id': None}, name='add_topic'),
    url('^topic/(?P<topic_id>\d+)/delete_posts/$', views.delete_posts, name='delete_posts'),
    url('^topic/(?P<topic_id>\d+)/move/$', views.move_topic, name='move_topic'),
    url('^topic/(?P<topic_id>\d+)/stick/$', views.stick_topic, name='stick_topic'),
    url('^topic/(?P<topic_id>\d+)/unstick/$', views.unstick_topic, name='unstick_topic'),
    url('^topic/(?P<topic_id>\d+)/close/$', views.close_topic, name='close_topic'),
    url('^topic/(?P<topic_id>\d+)/open/$', views.open_topic, name='open_topic'),

    # Post
    url('^topic/(?P<topic_id>\d+)/post/add/$', views.add_post,
        {'forum_id': None}, name='add_post'),
    url('^post/(?P<post_id>\d+)/$', views.show_post, name='post'),
    url('^post/(?P<post_id>\d+)/edit/$', views.edit_post, name='edit_post'),
    url('^post/(?P<post_id>\d+)/delete/$', views.delete_post, name='delete_post'),
    # Post preview
    url(r'^preview/$', views.post_preview),

    # Subscription
    url('^subscription/topic/(?P<topic_id>\d+)/delete/$', views.delete_subscription, name='forum_delete_subscription'),
    url('^subscription/topic/(?P<topic_id>\d+)/add/$', views.add_subscription, name='forum_add_subscription'),
    
    # Private messages
    url('^pm/new/$', views.create_pm, name='forum_create_pm'),
    url('^pm/outbox/$', views.pm_outbox, name='forum_pm_outbox'),
    url('^pm/inbox/$', views.pm_inbox, name='forum_pm_inbox'),
    url('^pm/show/(?P<pm_id>\d+)/$', views.show_pm, name='forum_show_pm'),
)
