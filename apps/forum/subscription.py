from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from apps.forum import settings as forum_settings

def notify_subscribers(post):
    from apps.forum.models import Post

    topic = post.topic
    if post != topic.head:
        for user in topic.subscribers.all():
            if user != post.user:
                subject = u'RE: %s' % topic.name
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = user.email
                text_content = text_version(post)
                #html_content = html_version(post)
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                #msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=True)


TEXT_TEMPLATE = _(u"""New reply from %(username)s to topic that you have subscribed on.
---
%(message)s
---
See topic: %(post_url)s
Unsubscribe %(unsubscribe_url)s""")

def text_version(post):
    data = TEXT_TEMPLATE % {
        'username': post.user.username,
        'message': post.body_text,
        'post_url': absolute_url(post.get_absolute_url()),
        'unsubscribe_url': absolute_url(reverse('forum_delete_subscription', args=[post.topic.id])),
    }
    return data

def absolute_url(uri):
    return 'http://%s%s' % (forum_settings.FORUM_HOST, uri)
