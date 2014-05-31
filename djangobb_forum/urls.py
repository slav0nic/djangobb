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
    #url('^search/$', forum_views.search, name='search'),
    url('^misc/$', forum_views.misc, name='misc'),
    url('^youtube/(?P<video_id>[\w-]+)/$', forum_views.show_youtube_video, name='show_youtube_video'),
    # User
    url('^settings/(?P<username>.*)/$', forum_views.settings, name='forum_settings'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', forum_views.show_topic, name='topic'),
    url('^topic/(?P<topic_id>\d+)/unread/$', forum_views.show_unread_posts, name='topic_unread'),
    url('^topic/(?P<topic_id>\d+)/title/$', forum_views.get_topic_title, name='topic_title'),
    url(r'^(?P<forum_id>\d+)/topic/add/$', forum_views.add_topic, name='add_topic'),
    url('^topic/(?P<topic_id>\d+)/delete_posts/$', forum_views.delete_posts, name='delete_posts'),
    url('^topic/move/$', forum_views.move_topic, name='move_topic'),
    url('^topic/(?P<topic_id>\d+)/move_posts/$', forum_views.move_posts, name='move_posts'),
    url('^topic/(?P<topic_id>\d+)/stick_unstick/(?P<action>[s|u])/$', forum_views.stick_unstick_topic, name='stick_unstick_topic'),
    url('^topic/(?P<topic_id>\d+)/open_close/(?P<action>[c|o])/$', forum_views.open_close_topic, name='open_close_topic'),

    # Post
    url('^post/(?P<post_id>\d+)/$', forum_views.show_post, name='post'),
    url('^post/(?P<post_id>\d+)/edit/$', forum_views.edit_post, name='edit_post'),
    url('^post/(?P<post_id>\d+)/delete/$', forum_views.delete_post, name='delete_post'),
    url('^post/(?P<post_id>\d+)/mark_spam/$', forum_views.mark_spam, name='mark_post_spam'),
    url('^post/(?P<post_id>\d+)/mark_ham/$', forum_views.mark_ham, name='mark_post_ham'),
    url('^post/(?P<post_id>\d+)/source/$', forum_views.get_post_source, name='post_source'),
    # Post preview
    url(r'^preview/$', forum_views.post_preview, name='post_preview'),

    # Reports
    url(r'^reports/$', forum_views.reports, name='forum_reports'),

    # Administration
    url(r'^admin/ajax/delete-all-posts/(?P<username>[-\w]+)/$', forum_views.delete_all_posts_by_user),
    url(r'^admin/ajax/post-count/(?P<username>[-\w]+)/$', forum_views.get_user_post_count),

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
        url('^m/$', forum_views.index, {'full':False}, name='mobile_index'),
        url('^m/signin/$', 'django.contrib.auth.views.login', {'template_name':'djangobb_forum/mobile/sign_in.html',}, name='mobile_sign_in'),
        #url('^m/search/$', forum_views.search, {'full':False}, name='mobile_search'),
        url('^m/(?P<forum_id>\d+)/$', forum_views.show_forum, {'full':False}, name='mobile_forum'),
        url('^m/(?P<forum_id>\d+)/topic/add/$', forum_views.add_topic, {'full':False}, name='mobile_add_topic'),
        url('^m/post/(?P<post_id>\d+)/$', forum_views.show_post, {'full':False}, name='mobile_post'),
        url('^m/post/(?P<post_id>\d+)/reply/$', forum_views.mobile_reply, name='mobile_reply'),
        url('^m/topic/(?P<topic_id>\d+)/$', forum_views.show_topic, {'full':False}, name='mobile_topic'),
        url('^m/topic/(?P<topic_id>\d+)/unread/$', forum_views.show_unread_posts, {'full':False}, name='mobile_topic_unread'),
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
