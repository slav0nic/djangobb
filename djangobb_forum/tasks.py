from django.contrib.auth.models import User
from django.db.models import F

from celery.decorators import task

from djangobb_forum.models import Topic

@task 
def scratch_notify_topic_subscribers(post_id):
    """
    Scratch task for notifying subscribers to a topic that someone has made a
    new post.
    """
    from notifications.models import SocialAction
    from djangobb_forum.models import Post
    try:
        post = Post.objects.select_related('topic').get(id=post_id)
    except Post.DoesNotExist:
        return
    topic = post.topic
    if post != topic.head:
        social_action = SocialAction(
            actor = post.user,
            object = topic,
        )
        social_action.save()

@task
def update_topic_on_view(user_id, topic_id, is_authenticated):
    """
    Update the views and reads for a topic - part of show_topic.
    Turned into async task to reduce page load times and increase
    scalability.
    """
    try:
        topic = Topic.objects.get(pk=topic_id)
        Topic.objects.filter(pk=topic_id).update(views=F('views') + 1)
        if is_authenticated:
            try:
                user = User.objects.get(pk=user_id)              
                topic.update_read(user)
            except User.DoesNotExist:
                pass
    except Topic.DoesNotExist:
        pass
