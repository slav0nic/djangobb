from celery.decorators import task

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
