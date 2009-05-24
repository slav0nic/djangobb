from datetime import datetime
from django.db.models.signals import post_save, pre_save, post_delete

from forum.subscription import notify_topic_subscribers, notify_pm_recipients
from forum.models import Topic, Post, PrivateMessage

def post_saved(instance, **kwargs):
    created = kwargs.get('created')
    post = instance
    if created:
        updated_time = datetime.now()
        post.topic.updated = updated_time
        post.topic.post_count = Post.objects.filter(topic=post.topic).count()
        post.topic.save(force_update=True)
        post.topic.forum.updated = updated_time
        post.topic.forum.post_count = Post.objects.filter(topic__forum=post.topic.forum).count()
        post.topic.forum.last_post = post
        post.topic.forum.save(force_update=True)
        notify_topic_subscribers(post)

def post_deleted(instance, **kwargs):
    post = instance
    post.topic.post_count = Post.objects.filter(topic=post.topic).count()
    post.topic.save()
    post.topic.forum.post_count = Post.objects.filter(topic__forum=post.topic.forum).count()
    post.topic.forum.save()

def pm_saved(instance, **kwargs):
    notify_pm_recipients(instance) 

def topic_saved(instance, **kwargs):
    created = kwargs.get('created')
    topic = instance
    if created:
        topic.forum.topic_count = topic.forum.topics.count()
        topic.forum.save(force_update=True)


post_save.connect(post_saved, sender=Post)
post_save.connect(pm_saved, sender=PrivateMessage)
post_save.connect(topic_saved, sender=Topic)

post_delete.connect(post_deleted, sender=Post)