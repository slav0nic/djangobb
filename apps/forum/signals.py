from forum.subscription import notify_topic_subscribers, notify_pm_recipients
from forum.models import Post, PrivateMessage

def post_saved(instance, **kwargs):
    notify_topic_subscribers(instance)
    
def pm_saved(instance, **kwargs):
    notify_pm_recipients(instance) 

post_save.connect(post_saved, sender=Post)
post_save.connect(pm_saved, sender=PrivateMessage)