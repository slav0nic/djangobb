# coding: utf-8
from __future__ import unicode_literals

from hashlib import sha1
import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import aggregates
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

import pytz

from djangobb_forum.fields import AutoOneToOneField, ExtendedImageField, JSONField
from djangobb_forum.util import smiles, convert_text_to_html
from djangobb_forum import settings as forum_settings

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^djangobb_forum\.fields\.AutoOneToOneField',
                                 '^djangobb_forum\.fields\.JSONField',
                                 '^djangobb_forum\.fields\.ExtendedImageField'])

TZ_CHOICES = [(tz_name, tz_name) for tz_name in pytz.common_timezones]

SIGN_CHOICES = (
    (1, 'PLUS'),
    (-1, 'MINUS'),
)

PRIVACY_CHOICES = (
    (0, _('Display your e-mail address.')),
    (1, _('Hide your e-mail address but allow form e-mail.')),
    (2, _('Hide your e-mail address and disallow form e-mail.')),
)

MARKUP_CHOICES = [('bbcode', 'bbcode')]
try:
    import markdown
    MARKUP_CHOICES.append(("markdown", "markdown"))
except ImportError:
    pass

path = os.path.join(settings.STATIC_ROOT, 'djangobb_forum', 'themes')
if os.path.exists(path):
    # fix for collectstatic
    THEME_CHOICES = [(theme, theme) for theme in os.listdir(path)
                     if os.path.isdir(os.path.join(path, theme))]
else:
    THEME_CHOICES = []

@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(_('Name'), max_length=80)
    groups = models.ManyToManyField(Group, blank=True, verbose_name=_('Groups'), help_text=_('Only users from these groups can see this category'))
    position = models.IntegerField(_('Position'), blank=True, default=0)

    class Meta:
        ordering = ['position']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

    def forum_count(self):
        return self.forums.all().count()

    @property
    def topics(self):
        return Topic.objects.filter(forum__category__id=self.id).select_related()

    @property
    def posts(self):
        return Post.objects.filter(topic__forum__category__id=self.id).select_related()

    def has_access(self, user):
        if user.is_superuser:
            return True
        if self.groups.exists():
            if user.is_authenticated():
                if not self.groups.filter(user__pk=user.id).exists():
                    return False
            else:
                return False
        return True


@python_2_unicode_compatible
class Forum(models.Model):
    category = models.ForeignKey(Category, related_name='forums', verbose_name=_('Category'))
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)
    description = models.TextField(_('Description'), blank=True, default='')
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, verbose_name=_('Moderators'))
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    topic_count = models.IntegerField(_('Topic count'), blank=True, default=0)
    last_post = models.ForeignKey('Post', related_name='last_forum_post', blank=True, null=True)
    forum_logo = ExtendedImageField(_('Forum Logo'), blank=True, default='',
                                    upload_to=forum_settings.FORUM_LOGO_UPLOAD_TO,
                                    width=forum_settings.FORUM_LOGO_WIDTH,
                                    height=forum_settings.FORUM_LOGO_HEIGHT)

    class Meta:
        ordering = ['position']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('djangobb:forum', [self.id])

    @property
    def posts(self):
        return Post.objects.filter(topic__forum__id=self.id).select_related()


@python_2_unicode_compatible
class Topic(models.Model):
    forum = models.ForeignKey(Forum, related_name='topics', verbose_name=_('Forum'))
    name = models.CharField(_('Subject'), max_length=255)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('User'))
    views = models.IntegerField(_('Views count'), blank=True, default=0)
    sticky = models.BooleanField(_('Sticky'), blank=True, default=False)
    closed = models.BooleanField(_('Closed'), blank=True, default=False)
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='subscriptions', verbose_name=_('Subscribers'), blank=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    last_post = models.ForeignKey('Post', related_name='last_topic_post', blank=True, null=True)

    class Meta:
        ordering = ['-updated']
        get_latest_by = 'updated'
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        try:
            last_post = self.posts.latest()
            last_post.last_forum_post.clear()
        except Post.DoesNotExist:
            pass
        else:
            last_post.last_forum_post.clear()
        forum = self.forum
        super(Topic, self).delete(*args, **kwargs)
        try:
            forum.last_post = Topic.objects.filter(forum__id=forum.id).latest().last_post
        except Topic.DoesNotExist:
            forum.last_post = None
        forum.topic_count = Topic.objects.filter(forum__id=forum.id).count()
        forum.post_count = Post.objects.filter(topic__forum__id=forum.id).count()
        forum.save()

    @property
    def head(self):
        try:
            return self.posts.select_related().order_by('created')[0]
        except IndexError:
            return None

    @property
    def reply_count(self):
        return self.post_count - 1

    @models.permalink
    def get_absolute_url(self):
        return ('djangobb:topic', [self.id])

    def update_read(self, user):
        tracking = user.posttracking
        #if last_read > last_read - don't check topics
        if tracking.last_read and (tracking.last_read > self.last_post.created):
            return
        if isinstance(tracking.topics, dict):
            #clear topics if len > 5Kb and set last_read to current time
            if len(tracking.topics) > 5120:
                tracking.topics = None
                tracking.last_read = timezone.now()
                tracking.save()
            #update topics if exist new post or does't exist in dict
            if self.last_post_id > tracking.topics.get(str(self.id), 0):
                tracking.topics[str(self.id)] = self.last_post_id
                tracking.save()
        else:
            #initialize topic tracking dict
            tracking.topics = {self.id: self.last_post_id}
            tracking.save()


@python_2_unicode_compatible
class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts', verbose_name=_('Topic'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posts', verbose_name=_('User'))
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('Updated by'), blank=True, null=True)
    markup = models.CharField(_('Markup'), max_length=15, default=forum_settings.DEFAULT_MARKUP, choices=MARKUP_CHOICES)
    body = models.TextField(_('Message'))
    body_html = models.TextField(_('HTML version'))
    user_ip = models.GenericIPAddressField(_('User IP'), blank=True, null=True)


    class Meta:
        ordering = ['created']
        get_latest_by = 'created'
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def save(self, *args, **kwargs):
        self.body_html = convert_text_to_html(self.body, self.markup)
        if forum_settings.SMILES_SUPPORT and self.user.forum_profile.show_smilies:
            self.body_html = smiles(self.body_html)
        super(Post, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        self_id = self.id
        head_post_id = self.topic.posts.order_by('created')[0].id
        forum = self.topic.forum
        topic = self.topic
        profile = self.user.forum_profile
        self.last_topic_post.clear()
        self.last_forum_post.clear()
        super(Post, self).delete(*args, **kwargs)
        #if post was last in topic - remove topic
        if self_id == head_post_id:
            topic.delete()
        else:
            try:
                topic.last_post = Post.objects.filter(topic__id=topic.id).latest()
            except Post.DoesNotExist:
                topic.last_post = None
            topic.post_count = Post.objects.filter(topic__id=topic.id).count()
            topic.save()
        try:
            forum.last_post = Post.objects.filter(topic__forum__id=forum.id).latest()
        except Post.DoesNotExist:
            forum.last_post = None
        #TODO: for speedup - save/update only changed fields
        forum.post_count = Post.objects.filter(topic__forum__id=forum.id).count()
        forum.topic_count = Topic.objects.filter(forum__id=forum.id).count()
        forum.save()
        profile.post_count = Post.objects.filter(user__id=self.user_id).count()
        profile.save()

    @models.permalink
    def get_absolute_url(self):
        return ('djangobb:post', [self.id])

    def summary(self):
        LIMIT = 50
        tail = len(self.body) > LIMIT and '...' or ''
        return self.body[:LIMIT] + tail

    __str__ = summary


@python_2_unicode_compatible
class Reputation(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reputations_from', verbose_name=_('From'))
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reputations_to', verbose_name=_('To'))
    post = models.ForeignKey(Post, related_name='post', verbose_name=_('Post'))
    time = models.DateTimeField(_('Time'), auto_now_add=True)
    sign = models.IntegerField(_('Sign'), choices=SIGN_CHOICES, default=0)
    reason = models.TextField(_('Reason'), max_length=1000)

    class Meta:
        verbose_name = _('Reputation')
        verbose_name_plural = _('Reputations')
        unique_together = (('from_user', 'post'),)

    def __str__(self):
        time = timezone.localtime(self.time)
        return 'T[%d], FU[%d], TU[%d]: %s' % (self.post.id, self.from_user.id, self.to_user.id, str(time))


class ProfileManager(models.Manager):
    use_for_related_fields = True
    def get_queryset(self):
        qs = super(ProfileManager, self).get_queryset()
        if forum_settings.REPUTATION_SUPPORT:
            qs = qs.extra(select={
                'reply_total': 'SELECT SUM(sign) FROM djangobb_forum_reputation WHERE to_user_id = djangobb_forum_profile.user_id GROUP BY to_user_id',
                'reply_count_minus': "SELECT SUM(sign) FROM djangobb_forum_reputation WHERE to_user_id = djangobb_forum_profile.user_id AND sign = '-1' GROUP BY to_user_id",
                'reply_count_plus': "SELECT SUM(sign) FROM djangobb_forum_reputation WHERE to_user_id = djangobb_forum_profile.user_id AND sign = '1' GROUP BY to_user_id",
                })
        return qs


class Profile(models.Model):
    user = AutoOneToOneField(settings.AUTH_USER_MODEL, related_name='forum_profile', verbose_name=_('User'))
    status = models.CharField(_('Status'), max_length=30, blank=True)
    site = models.URLField(_('Site'), blank=True)
    jabber = models.CharField(_('Jabber'), max_length=80, blank=True)
    icq = models.CharField(_('ICQ'), max_length=12, blank=True)
    msn = models.CharField(_('MSN'), max_length=80, blank=True)
    aim = models.CharField(_('AIM'), max_length=80, blank=True)
    yahoo = models.CharField(_('Yahoo'), max_length=80, blank=True)
    location = models.CharField(_('Location'), max_length=30, blank=True)
    signature = models.TextField(_('Signature'), blank=True, default='', max_length=forum_settings.SIGNATURE_MAX_LENGTH)
    signature_html = models.TextField(_('Signature'), blank=True, default='', max_length=forum_settings.SIGNATURE_MAX_LENGTH)
    time_zone = models.CharField(_('Time zone'),max_length=50, choices=TZ_CHOICES, default=settings.TIME_ZONE)
    language = models.CharField(_('Language'), max_length=5, default='', choices=settings.LANGUAGES)
    avatar = ExtendedImageField(_('Avatar'), blank=True, default='', upload_to=forum_settings.AVATARS_UPLOAD_TO, width=forum_settings.AVATAR_WIDTH, height=forum_settings.AVATAR_HEIGHT)
    theme = models.CharField(_('Theme'), choices=THEME_CHOICES, max_length=80, default='default')
    show_avatar = models.BooleanField(_('Show avatar'), blank=True, default=True)
    show_signatures = models.BooleanField(_('Show signatures'), blank=True, default=True)
    show_smilies = models.BooleanField(_('Show smilies'), blank=True, default=True)
    privacy_permission = models.IntegerField(_('Privacy permission'), choices=PRIVACY_CHOICES, default=1)
    auto_subscribe = models.BooleanField(_('Auto subscribe'), help_text=_("Auto subscribe all topics you have created or reply."), blank=True, default=False)
    markup = models.CharField(_('Default markup'), max_length=15, default=forum_settings.DEFAULT_MARKUP, choices=MARKUP_CHOICES)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)

    objects = ProfileManager()

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def last_post(self):
        posts = Post.objects.filter(user__id=self.user_id).order_by('-created')
        if posts:
            return posts[0].created
        else:
            return None


@python_2_unicode_compatible
class PostTracking(models.Model):
    """
    Model for tracking read/unread posts.
    In topics stored ids of topics and last_posts as dict.
    """

    user = AutoOneToOneField(settings.AUTH_USER_MODEL)
    topics = JSONField(null=True, blank=True)
    last_read = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Post tracking')
        verbose_name_plural = _('Post tracking')

    def __str__(self):
        return self.user.username


@python_2_unicode_compatible
class Report(models.Model):
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reported_by', verbose_name=_('Reported by'))
    post = models.ForeignKey(Post, verbose_name=_('Post'))
    zapped = models.BooleanField(_('Zapped'), blank=True, default=False)
    zapped_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='zapped_by', blank=True, null=True, verbose_name=_('Zapped by'))
    created = models.DateTimeField(_('Created'), blank=True)
    reason = models.TextField(_('Reason'), blank=True, default='', max_length='1000')

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')

    def __str__(self):
        return '%s %s' % (self.reported_by , self.zapped)


@python_2_unicode_compatible
class Ban(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_('Banned user'), related_name='ban_users')
    ban_start = models.DateTimeField(_('Ban start'), default=timezone.now)
    ban_end = models.DateTimeField(_('Ban end'), blank=True, null=True)
    reason = models.TextField(_('Reason'))

    class Meta:
        verbose_name = _('Ban')
        verbose_name_plural = _('Bans')

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.user.is_active = False
        self.user.save()
        super(Ban, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.user.is_active = True
        self.user.save()
        super(Ban, self).delete(*args, **kwargs)


@python_2_unicode_compatible
class Attachment(models.Model):
    post = models.ForeignKey(Post, verbose_name=_('Post'), related_name='attachments')
    size = models.IntegerField(_('Size'))
    content_type = models.CharField(_('Content type'), max_length=255)
    path = models.CharField(_('Path'), max_length=255)
    name = models.TextField(_('Name'))
    hash = models.CharField(_('Hash'), max_length=40, blank=True, default='', db_index=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if not self.hash:
            self.hash = sha1((str(self.id) + settings.SECRET_KEY).encode('ascii')).hexdigest()
        super(Attachment, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('djangobb:forum_attachment', [self.hash])

    def get_absolute_path(self):
        return os.path.join(settings.MEDIA_ROOT, forum_settings.ATTACHMENT_UPLOAD_TO,
                            self.path)


@python_2_unicode_compatible
class Poll(models.Model):
    topic = models.ForeignKey(Topic)
    question = models.CharField(max_length=200)
    choice_count = models.PositiveSmallIntegerField(default=1,
        help_text=_("How many choices are allowed simultaneously."),
    )
    active = models.BooleanField(default=True,
        help_text=_("Can users vote to this poll or just see the result?"),
    )
    deactivate_date = models.DateTimeField(null=True, blank=True,
        help_text=_("Point of time after this poll would be automatic deactivated"),
    )
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True,
        help_text=_("Users who has voted this poll."),
    )
    def deactivate_if_expired(self):
        if self.active and self.deactivate_date:
            now = timezone.now()
            if now > self.deactivate_date:
                self.active = False
                self.save()

    def single_choice(self):
        return self.choice_count == 1

    def __str__(self):
        return self.question


@python_2_unicode_compatible
class PollChoice(models.Model):
    poll = models.ForeignKey(Poll, related_name="choices")
    choice = models.CharField(max_length=200)
    votes = models.IntegerField(default=0, editable=False)

    def percent(self):
        if not self.votes:
            return 0.0
        result = PollChoice.objects.filter(poll=self.poll).aggregate(aggregates.Sum("votes"))
        votes_sum = result["votes__sum"]
        return float(self.votes) / votes_sum * 100

    def __str__(self):
        return self.choice



from .signals import post_saved, topic_saved

post_save.connect(post_saved, sender=Post, dispatch_uid='djangobb_post_save')
post_save.connect(topic_saved, sender=Topic, dispatch_uid='djangobb_topic_save')
