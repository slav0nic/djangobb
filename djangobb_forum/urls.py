from django.urls import re_path

from djangobb_forum import settings as forum_settings
from djangobb_forum import views as forum_views
from djangobb_forum.feeds import LastPosts, LastTopics, LastPostsOnForum, \
     LastPostsOnCategory, LastPostsOnTopic
from djangobb_forum.forms import EssentialsProfileForm, \
    PersonalProfileForm, MessagingProfileForm, PersonalityProfileForm, \
    DisplayProfileForm, PrivacyProfileForm, UploadAvatarForm


urlpatterns = [

    # Forum
    re_path('^$', forum_views.index, name='index'),
    re_path('^(?P<forum_id>\d+)/$', forum_views.show_forum, name='forum'),
    re_path('^moderate/(?P<forum_id>\d+)/$', forum_views.moderate, name='moderate'),
    re_path('^search/$', forum_views.search, name='search'),
    re_path('^misc/$', forum_views.misc, name='misc'),

    # User
    re_path('^user/(?P<username>.*)/upload_avatar/$', forum_views.upload_avatar, {
        'form_class': UploadAvatarForm,
        'template': 'djangobb_forum/upload_avatar.html'
        }, name='forum_profile_upload_avatar'),
    re_path('^user/(?P<username>.*)/privacy/$', forum_views.user, {
        'section': 'privacy',
        'form_class': PrivacyProfileForm,
        'template': 'djangobb_forum/profile/profile_privacy.html'
        }, name='forum_profile_privacy'),
    re_path('^user/(?P<username>.*)/display/$', forum_views.user, {
        'section': 'display',
        'form_class': DisplayProfileForm,
        'template': 'djangobb_forum/profile/profile_display.html'
        }, name='forum_profile_display'),
    re_path('^user/(?P<username>.*)/personality/$', forum_views.user, {
        'section': 'personality',
        'form_class': PersonalityProfileForm,
        'template': 'djangobb_forum/profile/profile_personality.html'
        }, name='forum_profile_personality'),
    re_path('^user/(?P<username>.*)/messaging/$', forum_views.user, {
        'section': 'messaging',
        'form_class': MessagingProfileForm,
        'template': 'djangobb_forum/profile/profile_messaging.html'
        }, name='forum_profile_messaging'),
    re_path('^user/(?P<username>.*)/personal/$', forum_views.user, {
        'section': 'personal',
        'form_class': PersonalProfileForm,
        'template': 'djangobb_forum/profile/profile_personal.html'
        }, name='forum_profile_personal'),
    re_path('^user/(?P<username>.*)/essentials/$', forum_views.user, name='forum_profile_essentials'),
    re_path('^user/(?P<username>.*)/$', forum_views.user, name='forum_profile'),
    re_path('^users/$', forum_views.users, name='forum_users'),

    # Topic
    re_path('^topic/(?P<topic_id>\d+)/$', forum_views.show_topic, name='topic'),
    re_path('^(?P<forum_id>\d+)/topic/add/$', forum_views.add_topic, name='add_topic'),
    re_path('^topic/(?P<topic_id>\d+)/delete_posts/$', forum_views.delete_posts, name='delete_posts'),
    re_path('^topic/move/$', forum_views.move_topic, name='move_topic'),
    re_path('^topic/(?P<topic_id>\d+)/stick_unstick/(?P<action>[s|u])/$', forum_views.stick_unstick_topic, name='stick_unstick_topic'),
    re_path('^topic/(?P<topic_id>\d+)/open_close/(?P<action>[c|o])/$', forum_views.open_close_topic, name='open_close_topic'),

    # Post
    re_path('^post/(?P<post_id>\d+)/$', forum_views.show_post, name='post'),
    re_path('^post/(?P<post_id>\d+)/edit/$', forum_views.edit_post, name='edit_post'),
    re_path('^post/(?P<post_id>\d+)/delete/$', forum_views.delete_post, name='delete_post'),
    # Post preview
    re_path(r'^preview/$', forum_views.post_preview, name='post_preview'),

    # Subscription
    re_path('^subscription/topic/(?P<topic_id>\d+)/delete/$', forum_views.delete_subscription, name='forum_delete_subscription'),
    re_path('^subscription/topic/(?P<topic_id>\d+)/add/$', forum_views.add_subscription, name='forum_add_subscription'),

    # Feeds
    re_path(r'^feeds/posts/$', LastPosts(), name='forum_posts_feed'),
    re_path(r'^feeds/topics/$', LastTopics(), name='forum_topics_feed'),
    re_path(r'^feeds/topic/(?P<topic_id>\d+)/$', LastPostsOnTopic(), name='forum_topic_feed'),
    re_path(r'^feeds/forum/(?P<forum_id>\d+)/$', LastPostsOnForum(), name='forum_forum_feed'),
    re_path(r'^feeds/category/(?P<category_id>\d+)/$', LastPostsOnCategory(), name='forum_category_feed'),
]

### EXTENSIONS ###

# LOFI Extension
if (forum_settings.LOFI_SUPPORT):
    urlpatterns += [
        re_path('^lofi/$', forum_views.index, {'full':False}, name='lofi_index'),
        re_path('^(?P<forum_id>\d+)/lofi/$', forum_views.show_forum, {'full':False}, name='lofi_forum'),
        re_path('^topic/(?P<topic_id>\d+)/lofi/$', forum_views.show_topic, {'full':False}, name='lofi_topic'),
    ]

# REPUTATION Extension
if (forum_settings.REPUTATION_SUPPORT):
    urlpatterns += [
        re_path('^reputation/(?P<username>.*)/$', forum_views.reputation, name='reputation'),
    ]

# ATTACHMENT Extension
if (forum_settings.ATTACHMENT_SUPPORT):
    urlpatterns += [
        re_path('^attachment/(?P<hash>\w+)/$', forum_views.show_attachment, name='forum_attachment'),
    ]
