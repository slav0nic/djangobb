from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from apps.forum import settings as forum_settings
from apps.forum.util import absolute_url

TOPIC_SUBSCRIPTION_TEXT_TEMPLATE = (u"""New reply from %(username)s to topic that you have subscribed on.
---
%(message)s
---
See topic: %(post_url)s
Unsubscribe %(unsubscribe_url)s""")

PM_RECIPIENT_TEXT_TEMPLATE = (u"""User %(username)s have sent your the new private message.
---
%(message)s
---
See message online: %(pm_url)s""")


def send_mail(rec_list, subject, text, html=None):
    """
    Shortcut for sending email.
    """

    from_email = settings.DEFAULT_FROM_EMAIL

    msg = EmailMultiAlternatives(subject, text, from_email, rec_list)
    if html:
        msg.attach_alternative(html, "text/html")
    if forum_settings.EMAIL_DEBUG:
        print '---begin---'
        print 'To:', rec_list
        print 'Subject:', subject
        print 'Body:', text
        print '---end---'
    else:
        msg.send(fail_silently=True)


def notify_topic_subscribers(post):
    from apps.forum.models import Post

    topic = post.topic
    if post != topic.head:
        for user in topic.subscribers.all():
            if user != post.user:
                subject = u'RE: %s' % topic.name
                to_email = user.email
                text_content = TOPIC_SUBSCRIPTION_TEXT_TEMPLATE % {
                        'username': post.user.username,
                        'message': post.body_text,
                        'post_url': absolute_url(post.get_absolute_url()),
                        'unsubscribe_url': absolute_url(reverse('forum_delete_subscription', args=[post.topic.id])),
                    }
                #html_content = html_version(post)
                send_mail([to_email], subject, text_content)


def notify_pm_recipients(pm):
    if not pm.read:
        from apps.forum.models import PrivateMessage 
        subject = (u'There are new messages')
        to_email = pm.dst_user.email
        text_content = PM_RECIPIENT_TEXT_TEMPLATE % {
            'username': pm.src_user.username,
            'message': pm.body_text,
            'pm_url': absolute_url(pm.get_absolute_url()),
         }
        send_mail([to_email], subject, text_content)
