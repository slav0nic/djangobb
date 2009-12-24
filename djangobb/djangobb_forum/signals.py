from datetime import datetime

from django.db.models.signals import post_save, pre_save, post_delete

from djangobb_forum.subscription import notify_topic_subscribers, notify_pm_recipients
from djangobb_forum.models import Topic, Post, PrivateMessage


def post_saved(instance, **kwargs):
    created = kwargs.get('created')
    post = instance
    topic = post.topic

    if created:
        topic.last_post = post
        topic.post_count = topic.posts.count()
        profile = post.user.forum_profile
        profile.post_count = post.user.posts.count()
        profile.save(force_update=True)
        notify_topic_subscribers(post)
    topic.save(force_update=True)


def pm_saved(instance, **kwargs):
    notify_pm_recipients(instance) 


def topic_saved(instance, **kwargs):
    created = kwargs.get('created')
    topic = instance
    forum = topic.forum
    forum.topic_count = forum.topics.count()
    forum.updated = topic.updated
    forum.post_count = forum.posts.count()
    forum.last_post = topic.last_post
    forum.save(force_update=True)


post_save.connect(post_saved, sender=Post)
post_save.connect(pm_saved, sender=PrivateMessage)
post_save.connect(topic_saved, sender=Topic)
