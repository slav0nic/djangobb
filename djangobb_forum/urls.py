from django.conf.urls.defaults import *

from djangobb_forum import settings as forum_settings
from djangobb_forum import views as forum_views
from djangobb_forum.feeds import LastPosts, LastTopics, LastPostsOnForum, \
     LastPostsOnCategory, LastPostsOnTopic
from djangobb_forum.forms import EssentialsProfileForm, \
    PersonalProfileForm, MessagingProfileForm, PersonalityProfileForm, \
    DisplayProfileForm, PrivacyProfileForm, UploadAvatarForm


urlpatterns = patterns('',

    # Forum
    url('^$', forum_views.index, name='index'),
    url('^(?P<forum_id>\d+)/$', forum_views.show_forum, name='forum'),
    url('^moderate/(?P<forum_id>\d+)/$', forum_views.moderate, name='moderate'),
    url('^search/$', forum_views.search, name='search'),
    url('^misc/$', forum_views.misc, name='misc'),
    url('^youtube/(?P<video_id>[\w-]+)/$', forum_views.show_youtube_video, name='show_youtube_video'),
    # User
    url('^user/(?P<username>.*)/settings/$', forum_views.user, {
        'section': 'personality',
        'form_class': PersonalityProfileForm,
        'template': 'djangobb_forum/profile/profile_personality.html'
        }, name='forum_profile_personality'),
    url('^user/(?P<username>.*)/$', forum_views.user, name='forum_profile'),
    url('^users/$', forum_views.users, name='forum_users'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', forum_views.show_topic, name='topic'),
    url('^topic/(?P<topic_id>\d+)/title/$', forum_views.get_topic_title, name='topic_title'),
    url('^(?P<forum_id>\d+)/topic/add/$', forum_views.add_topic, name='add_topic'),
    url('^topic/(?P<topic_id>\d+)/delete_posts/$', forum_views.delete_posts, name='delete_posts'),
    url('^topic/move/$', forum_views.move_topic, name='move_topic'),
    url('^topic/(?P<topic_id>\d+)/move_posts/$', forum_views.move_posts, name='move_posts'),
    url('^topic/(?P<topic_id>\d+)/stick_unstick/(?P<action>[s|u])/$', forum_views.stick_unstick_topic, name='stick_unstick_topic'),
    url('^topic/(?P<topic_id>\d+)/open_close/(?P<action>[c|o])/$', forum_views.open_close_topic, name='open_close_topic'),

    # Post
    url('^post/(?P<post_id>\d+)/$', forum_views.show_post, name='post'),
    url('^post/(?P<post_id>\d+)/edit/$', forum_views.edit_post, name='edit_post'),
    url('^post/(?P<post_id>\d+)/delete/$', forum_views.delete_post, name='delete_post'),
    url('^post/(?P<post_id>\d+)/source/$', forum_views.get_post_source, name='post_source'),
    # Post preview
    url(r'^preview/$', forum_views.post_preview, name='post_preview'),

    # Reports
    url(r'^reports/$', forum_views.reports, name='forum_reports'),

    # Subscription
    url('^subscription/topic/(?P<topic_id>\d+)/delete/$', forum_views.delete_subscription, name='forum_delete_subscription'),
    url('^subscription/topic/(?P<topic_id>\d+)/add/$', forum_views.add_subscription, name='forum_add_subscription'),

    # Feeds
    url(r'^feeds/posts/$', LastPosts(), name='forum_posts_feed'),
    url(r'^feeds/topics/$', LastTopics(), name='forum_topics_feed'),
    url(r'^feeds/topic/(?P<topic_id>\d+)/$', LastPostsOnTopic(), name='forum_topic_feed'),
    url(r'^feeds/forum/(?P<forum_id>\d+)/$', LastPostsOnForum(), name='forum_forum_feed'),
    url(r'^feeds/category/(?P<category_id>\d+)/$', LastPostsOnCategory(), name='forum_category_feed'),
)

### EXTENSIONS ###

# LOFI Extension
if (forum_settings.LOFI_SUPPORT):
    urlpatterns += patterns('',
        url('^lofi/$', forum_views.index, {'full':False}, name='lofi_index'),
        url('^lofi/signin/$', 'django.contrib.auth.views.login', {'template_name':'djangobb_forum/lofi/sign_in.html',}, name='lofi_sign_in'),
        url('^search/lofi/$', forum_views.search, {'full':False}, name='lofi_search'),
        url('^(?P<forum_id>\d+)/lofi/$', forum_views.show_forum, {'full':False}, name='lofi_forum'),
        url('^(?P<forum_id>\d+)/topic/add/lofi/$', forum_views.add_topic, {'full':False}, name='lofi_add_topic'),
        url('^post/(?P<post_id>\d+)/lofi/$', forum_views.show_post, {'full':False}, name='lofi_post'),
        url('^post/(?P<post_id>\d+)/reply/lofi/$', forum_views.lofi_reply, name='lofi_reply'),
        url('^topic/(?P<topic_id>\d+)/lofi/$', forum_views.show_topic, {'full':False}, name='lofi_topic'),
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
