# coding: utf-8

from hashlib import sha1
import os

from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models import aggregates
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from django_fsm.db.fields import FSMField, transition, can_proceed

from djangobb_forum.fields import AutoOneToOneField, ExtendedImageField, JSONField
from djangobb_forum.util import smiles, convert_text_to_html
from djangobb_forum import settings as forum_settings

if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ['^djangobb_forum\.fields\.AutoOneToOneField',
                                 '^djangobb_forum\.fields\.JSONField',
                                 '^djangobb_forum\.fields\.ExtendedImageField'])

TZ_CHOICES = [(float(x[0]), x[1]) for x in (
    (-12, '-12'), (-11, '-11'), (-10, '-10'), (-9.5, '-09.5'), (-9, '-09'),
    (-8.5, '-08.5'), (-8, '-08 PST'), (-7, '-07 MST'), (-6, '-06 CST'),
    (-5, '-05 EST'), (-4, '-04 AST'), (-3.5, '-03.5'), (-3, '-03 ADT'),
    (-2, '-02'), (-1, '-01'), (0, '00 GMT'), (1, '+01 CET'), (2, '+02'),
    (3, '+03'), (3.5, '+03.5'), (4, '+04'), (4.5, '+04.5'), (5, '+05'),
    (5.5, '+05.5'), (6, '+06'), (6.5, '+06.5'), (7, '+07'), (8, '+08'),
    (9, '+09'), (9.5, '+09.5'), (10, '+10'), (10.5, '+10.5'), (11, '+11'),
    (11.5, '+11.5'), (12, '+12'), (13, '+13'), (14, '+14'),
)]

SIGN_CHOICES = (
    (1, 'PLUS'),
    (-1, 'MINUS'),
)

PRIVACY_CHOICES = (
    (0, _(u'Display your e-mail address.')),
    (1, _(u'Hide your e-mail address but allow form e-mail.')),
    (2, _(u'Hide your e-mail address and disallow form e-mail.')),
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


import logging
logger = logging.getLogger(__name__)

akismet_api = None
try:
    from akismet import Akismet
    akismet_api = Akismet(key=forum_settings.AKISMET_API_KEY, blog_url=forum_settings.AKISMET_BLOG_URL, agent=forum_settings.AKISMET_AGENT)
    if not akismet_api.verify_key():
        logger.error("Invalid Aksimet API key.", extra={'key': akismet_api.key, 'blog': akismet_api.blog_url, 'user_agent': akismet_api.user_agent})
        akismet_api = None
except Exception as e:
    logger.error("Error while initializing Akismet", extra={'exception': e})


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=80)
    groups = models.ManyToManyField(Group, blank=True, null=True, verbose_name=_('Groups'), help_text=_('Only users from these groups can see this category'))
    position = models.IntegerField(_('Position'), blank=True, default=0)

    class Meta:
        ordering = ['position']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
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


class Forum(models.Model):
    category = models.ForeignKey(Category, related_name='forums', verbose_name=_('Category'))
    moderator_only = models.BooleanField(_('New topics by moderators only'), default=False)
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)
    description = models.TextField(_('Description'), blank=True, default='')
    moderators = models.ManyToManyField(User, blank=True, null=True, verbose_name=_('Moderators'))
    updated = models.DateTimeField(_('Updated'), auto_now=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    topic_count = models.IntegerField(_('Topic count'), blank=True, default=0)
    last_post = models.ForeignKey('Post', related_name='last_forum_post', blank=True, null=True)

    class Meta:
        ordering = ['position']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('djangobb:forum', [self.id])

    def get_mobile_url(self):
        return reverse('djangobb:mobile_forum', args=[self.id])

    @property
    def posts(self):
        return Post.objects.filter(topic__forum__id=self.id).select_related()

    def set_last_post(self):
        try:
            self.last_post = Topic.objects.filter(forum=self).latest().last_post
        except Topic.DoesNotExist:
            self.last_post = None

    def set_counts(self):
        self.topic_count = Topic.objects.filter(forum=self).count()
        self.post_count = Post.objects.filter(topic__forum=self).count()


class Topic(models.Model):
    forum = models.ForeignKey(Forum, related_name='topics', verbose_name=_('Forum'))
    name = models.CharField(_('Subject'), max_length=255)
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), null=True)
    user = models.ForeignKey(User, verbose_name=_('User'))
    views = models.IntegerField(_('Views count'), blank=True, default=0)
    sticky = models.BooleanField(_('Sticky'), blank=True, default=False)
    closed = models.BooleanField(_('Closed'), blank=True, default=False)
    subscribers = models.ManyToManyField(User, related_name='subscriptions', verbose_name=_('Subscribers'), blank=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    last_post = models.ForeignKey('Post', related_name='last_topic_post', blank=True, null=True)

    class Meta:
        ordering = ['-updated']
        get_latest_by = 'updated'
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        permissions = (
            ('delayed_close', 'Can close topics after a delay'),
            )

    def __unicode__(self):
        return self.name

    def move_to(self, new_forum):
        """
        Move a topic to a new forum.
        """
        self.clear_last_forum_post()
        old_forum = self.forum
        self.forum = new_forum
        self.save()
        old_forum.set_last_post()
        old_forum.set_counts()
        old_forum.save()

    def delete(self, *args, **kwargs):
        self.clear_last_forum_post()
        forum = self.forum
        if forum_settings.SOFT_DELETE_TOPICS and (self.forum != get_object_or_404(Forum, pk=forum_settings.SOFT_DELETE_TOPICS) or not kwargs.get('staff', False)):
            self.forum = get_object_or_404(Forum, pk=forum_settings.SOFT_DELETE_TOPICS)
            self.save()
        else:
            super(Topic, self).delete()

        forum.set_last_post()
        forum.set_counts()
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

    def get_mobile_url(self):
        return reverse('djangobb:mobile_topic', args=[self.id])

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
            elif self.last_post_id > tracking.topics.get(str(self.id), 0):
                tracking.topics[str(self.id)] = self.last_post_id
                tracking.save()
        else:
            #initialize topic tracking dict
            tracking.topics = {self.id: self.last_post_id}
            tracking.save()

    def clear_last_forum_post(self):
        """
        Prep for moving/deleting. Update the forum the topic belongs to.
        """
        try:
            last_post = self.posts.latest()
            last_post.last_forum_post.clear()
        except Post.DoesNotExist:
            pass
        else:
            last_post.last_forum_post.clear()


class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts', verbose_name=_('Topic'))
    user = models.ForeignKey(User, related_name='posts', verbose_name=_('User'))
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True)
    updated_by = models.ForeignKey(User, verbose_name=_('Updated by'), blank=True, null=True)
    markup = models.CharField(_('Markup'), max_length=15, default=forum_settings.DEFAULT_MARKUP, choices=MARKUP_CHOICES)
    body = models.TextField(_('Message'))
    body_html = models.TextField(_('HTML version'))
    user_ip = models.IPAddressField(_('User IP'), blank=True, null=True)


    class Meta:
        ordering = ['created']
        get_latest_by = 'created'
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        permissions = (
            ('fast_post', 'Can add posts without a time limit'),
            ('med_post', 'Can add posts at medium speed'),
            ('post_external_links', 'Can post external links'),
            ('delayed_delete', 'Can delete posts after a delay'),
            )

    def save(self, *args, **kwargs):
        self.body_html = convert_text_to_html(self.body, self.user.forum_profile)
        if forum_settings.SMILES_SUPPORT and self.user.forum_profile.show_smilies:
            self.body_html = smiles(self.body_html)
        super(Post, self).save(*args, **kwargs)

    def move_to(self, to_topic):
        delete_topic = (self.topic.posts.count() == 1)
        prev_topic = self.topic
        self.topic = to_topic
        self.save()
        self.set_counts()

        if delete_topic:
            prev_topic.delete()
        prev_topic.forum.set_last_post()
        prev_topic.forum.set_counts()
        prev_topic.forum.save()

    def delete(self, *args, **kwargs):
        self_id = self.id
        head_post_id = self.topic.posts.order_by('created')[0].id
        forum = self.topic.forum
        topic = self.topic
        profile = self.user.forum_profile
        self.last_topic_post.clear()
        self.last_forum_post.clear()

        # If we actually delete the post, we lose any reports that my have come from it. Also, there is no recovery (but I don't care about that as much right now)
        if self_id == head_post_id:
            topic.delete(*args, **kwargs)
        else:
            if forum_settings.SOFT_DELETE_POSTS and (self.topic != get_object_or_404(Topic, pk=forum_settings.SOFT_DELETE_POSTS) or not kwargs.get('staff', False)):
                    self.topic = get_object_or_404(Topic, pk=forum_settings.SOFT_DELETE_POSTS)
                    self.save()
            else:
                super(Post, self).delete()
                #if post was last in topic - remove topic
            try:
                topic.last_post = Post.objects.filter(topic__id=topic.id).latest()
            except Post.DoesNotExist:
                topic.last_post = None
            topic.post_count = Post.objects.filter(topic__id=topic.id).count()
            topic.save()
        forum.set_last_post()
        forum.save()
        self.set_counts()

    def set_counts(self):
        """
        Recounts this post's forum and and topic post counts.
        """
        forum = self.topic.forum
        profile = self.user.forum_profile
        #TODO: for speedup - save/update only changed fields
        forum.set_counts()
        forum.save()
        profile.set_counts()
        profile.save()

    @models.permalink
    def get_absolute_url(self):
        return ('djangobb:post', [self.id])

    def get_mobile_url(self):
        return reverse('djangobb:mobile_post', args=[self.id])

    def summary(self):
        LIMIT = 50
        tail = len(self.body) > LIMIT and '...' or ''
        return self.body[:LIMIT] + tail

    __unicode__ = summary


class Reputation(models.Model):
    from_user = models.ForeignKey(User, related_name='reputations_from', verbose_name=_('From'))
    to_user = models.ForeignKey(User, related_name='reputations_to', verbose_name=_('To'))
    post = models.ForeignKey(Post, related_name='post', verbose_name=_('Post'))
    time = models.DateTimeField(_('Time'), auto_now_add=True)
    sign = models.IntegerField(_('Sign'), choices=SIGN_CHOICES, default=0)
    reason = models.TextField(_('Reason'), max_length=1000)

    class Meta:
        verbose_name = _('Reputation')
        verbose_name_plural = _('Reputations')
        unique_together = (('from_user', 'post'),)

    def __unicode__(self):
        return u'T[%d], FU[%d], TU[%d]: %s' % (self.post.id, self.from_user.id, self.to_user.id, unicode(self.time))


class ProfileManager(models.Manager):
    use_for_related_fields = True
    def get_query_set(self):
        qs = super(ProfileManager, self).get_query_set()
        if forum_settings.REPUTATION_SUPPORT:
            qs = qs.extra(select={
                'reply_total': 'SELECT SUM(sign) FROM djangobb_forum_reputation WHERE to_user_id = djangobb_forum_profile.user_id GROUP BY to_user_id',
                'reply_count_minus': "SELECT SUM(sign) FROM djangobb_forum_reputation WHERE to_user_id = djangobb_forum_profile.user_id AND sign = '-1' GROUP BY to_user_id",
                'reply_count_plus': "SELECT SUM(sign) FROM djangobb_forum_reputation WHERE to_user_id = djangobb_forum_profile.user_id AND sign = '1' GROUP BY to_user_id",
                })
        return qs

class Profile(models.Model):
    user = AutoOneToOneField(User, related_name='forum_profile', verbose_name=_('User'))
    status = models.CharField(_('Status'), max_length=30, blank=True)
    site = models.URLField(_('Site'), verify_exists=False, blank=True)
    jabber = models.CharField(_('Jabber'), max_length=80, blank=True)
    icq = models.CharField(_('ICQ'), max_length=12, blank=True)
    msn = models.CharField(_('MSN'), max_length=80, blank=True)
    aim = models.CharField(_('AIM'), max_length=80, blank=True)
    yahoo = models.CharField(_('Yahoo'), max_length=80, blank=True)
    location = models.CharField(_('Location'), max_length=30, blank=True)
    signature = models.TextField(_('Signature'), blank=True, default='', max_length=forum_settings.SIGNATURE_MAX_LENGTH)
    signature_html = models.TextField(_('Signature'), blank=True, default='', max_length=forum_settings.SIGNATURE_MAX_LENGTH)
    time_zone = models.FloatField(_('Time zone'), choices=TZ_CHOICES, default=float(forum_settings.DEFAULT_TIME_ZONE))
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
            return  None

    def set_counts(self):
        self.post_count = Post.objects.filter(user=self.user).count()


class PostTracking(models.Model):
    """
    Model for tracking read/unread posts.
    In topics stored ids of topics and last_posts as dict.
    """

    user = AutoOneToOneField(User)
    topics = JSONField(null=True, blank=True)
    last_read = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Post tracking')
        verbose_name_plural = _('Post tracking')

    def __unicode__(self):
        return self.user.username

class Report(models.Model):
    reported_by = models.ForeignKey(User, related_name='reported_by', verbose_name=_('Reported by'))
    post = models.ForeignKey(Post, verbose_name=_('Post'))
    zapped = models.BooleanField(_('Zapped'), blank=True, default=False)
    zapped_by = models.ForeignKey(User, related_name='zapped_by', blank=True, null=True, verbose_name=_('Zapped by'))
    created = models.DateTimeField(_('Created'), blank=True)
    reason = models.TextField(_('Reason'), blank=True, default='', max_length='1000')

    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')

    def __unicode__(self):
        return u'%s %s' % (self.reported_by , self.zapped)

class Ban(models.Model):
    user = models.OneToOneField(User, verbose_name=_('Banned user'), related_name='ban_users')
    ban_start = models.DateTimeField(_('Ban start'), default=timezone.now)
    ban_end = models.DateTimeField(_('Ban end'), blank=True, null=True)
    reason = models.TextField(_('Reason'))

    class Meta:
        verbose_name = _('Ban')
        verbose_name_plural = _('Bans')

    def __unicode__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        self.user.is_active = False
        self.user.save()
        super(Ban, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.user.is_active = True
        self.user.save()
        super(Ban, self).delete(*args, **kwargs)


class Attachment(models.Model):
    post = models.ForeignKey(Post, verbose_name=_('Post'), related_name='attachments')
    size = models.IntegerField(_('Size'))
    content_type = models.CharField(_('Content type'), max_length=255)
    path = models.CharField(_('Path'), max_length=255)
    name = models.TextField(_('Name'))
    hash = models.CharField(_('Hash'), max_length=40, blank=True, default='', db_index=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Attachment, self).save(*args, **kwargs)
        if not self.hash:
            self.hash = sha1(str(self.id) + settings.SECRET_KEY).hexdigest()
        super(Attachment, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('djangobb:forum_attachment', [self.hash])

    def get_absolute_path(self):
        return os.path.join(settings.MEDIA_ROOT, forum_settings.ATTACHMENT_UPLOAD_TO,
                            self.path)


#------------------------------------------------------------------------------


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
    users = models.ManyToManyField(User, blank=True, null=True,
        help_text=_("Users who has voted this poll."),
    )
    def auto_deactivate(self):
        if self.active and self.deactivate_date:
            now = timezone.now()
            if now > self.deactivate_date:
                self.active = False
                self.save()

    def __unicode__(self):
        return self.question


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

    def __unicode__(self):
        return self.choice


#------------------------------------------------------------------------------


class PostStatusManager(models.Manager):
    def create_for_post(self, post, **kwargs):
        user_agent = kwargs.get("HTTP_USER_AGENT", None)
        referrer = kwargs.get("HTTP_REFERER", None)
        permalink = kwargs.get("permalink", None)
        return self.create(
            post=post, topic=post.topic, forum=post.topic.forum,
            user_agent=user_agent, referrer=referrer, permalink=permalink)

    def review_posts(self, posts, certainly_spam=False):
        for post in posts:
            try:
                post_status = post.poststatus
            except PostStatus.DoesNotExist:
                post_status = self.create_for_post(post)
            post_status.review(certainly_spam=certainly_spam)

    def review_new_posts(self):
        unreviewed = self.filter(state=PostStatus.UNREVIEWED)
        for post_status in unreviewed:
            post_status.review()
        return unreviewed


class PostStatus(models.Model):
    """
    Keeps track of the status of posts for moderation purposes.
    """
    UNREVIEWED = 'unreviewed'
    FILTERED_SPAM = 'filtered_spam'
    FILTERED_HAM = 'filtered_ham'
    MARKED_SPAM = 'marked_spam'
    MARKED_HAM = 'marked_ham'

    post = models.OneToOneField(Post, db_index=True)
    state = FSMField(default=UNREVIEWED)
    topic = models.ForeignKey(Topic) # Original topic
    forum = models.ForeignKey(Forum) # Original forum
    user_agent = models.CharField(max_length=200, blank=True, null=True)
    referrer = models.CharField(max_length=200, blank=True, null=True)
    permalink = models.CharField(max_length=200, blank=True, null=True)

    objects = PostStatusManager()

    spam_category = None
    spam_forum = None
    spam_topic = None

    def _get_spam_dustbin(self):
        if self.spam_category is None:
            self.spam_category, _ = Category.objects.get_or_create(
                name=forum_settings.SPAM_CATEGORY_NAME)

        if self.spam_forum is None:
            self.spam_forum, _ = Forum.objects.get_or_create(
                category=self.spam_category,
                name=forum_settings.SPAM_FORUM_NAME)

        if self.spam_topic is None:
            filterbot = User.objects.get_by_natural_key("filterbot")
            self.spam_topic, _ = Topic.objects.get_or_create(
                forum=self.spam_forum, name=forum_settings.SPAM_TOPIC_NAME,
                user=filterbot)

        return (self.spam_topic, self.spam_forum)

    def _undelete_post(self):
        """
        If the post is in the spam dustbin, move it back to its original location.
        """
        spam_topic, spam_forum = self._get_spam_dustbin()
        post = self.post
        topic = self.topic
        head = post.topic.head

        if post == head:
            topic.move_to(self.forum)
        else:
            post.move_to(self.topic)

    def _delete_post(self):
        """
        Move the post to the spam dustbin.
        """
        spam_topic, spam_forum = self._get_spam_dustbin()
        post = self.post
        topic = self.topic
        head = topic.head

        if post == head:
            topic.move_to(spam_forum)
        else:
            post.move_to(spam_topic)

    def to_akismet_data(self):
        post = self.post
        topic = self.topic
        user = post.user
        user_ip = post.user_ip
        comment_author = user.username
        user_agent = self.user_agent
        referrer = self.referrer
        permalink = self.permalink
        comment_date_gmt = post.created.isoformat(' ')
        comment_post_modified_gmt = topic.created.isoformat(' ')

        return {
            'user_ip': user_ip,
            'user_agent': user_agent,
            'comment_author': comment_author,
            'referrer': referrer,
            'permalink': permalink,
            'comment_type': 'comment',
            'comment_date_gmt': comment_date_gmt,
            'comment_post_modified_gmt': comment_post_modified_gmt
        }

    def _comment_check(self):
        """
        Pass the associated post through Akismet if it's available. If it's not
        available return None. Otherwise return True or False.
        """
        if akismet_api is None:
            logger.warning("Skipping akismet check. No api.")
            return None

        data = self.to_akismet_data()
        content = self.post.body
        is_spam = None

        try:
            is_spam = akismet_api.comment_check(body, data)
        except Exception as e:
            logger.error("Error while checking Akismet", extra={"exception": e})
            is_spam = None

        return is_spam

    def _submit_comment(self, report_type):
        """
        Report this post to Akismet as spam or ham. Raises an exception if it
        fails. report_type is 'spam' or 'ham'. Used by report_spam/report_ham.
        """
        if akismet_api is None:
            raise AkismetError("Can't submit to Akismet. No API.")

        data = self.to_akismet_data()
        content = self.post.body

        if report_type == "spam":
            akismet_api.submit_spam(content, data)

        elif report_type == "ham":
            akismet_api.submit_ham(content, data)
        else:
            raise NotImplementedError(
                "You're trying to report an unsupported comment type.")

    def _submit_spam(self):
        """
        Report this post to Akismet as spam.
        """
        self._submit_comment("spam")

    def _submit_ham(self):
        """
        Report this post to Akismet as ham.
        """
        self._submit_comment("ham")

    def is_spam(self):
        """
        Condition used by the FSM. Return True if the Akismet API is available
        and returns a positive. Otherwise return False or None.
        """
        is_spam = self._comment_check()
        if is_spam is None:
            return False
        else:
            return is_spam

    def is_ham(self):
        """
        Inverse of is_spam.
        """
        is_spam = self._comment_check()
        if is_spam is None:
            return False
        else:
            return not is_spam

    @transition(
        field=state, source=UNREVIEWED, target=FILTERED_SPAM,
        save=True, conditions=[is_spam])
    def filter_spam(self):
        """
        Akismet detected this post is spam, move it to the dustbin and report it.
        """
        self._delete_post()

    @transition(
        field=state, source=UNREVIEWED, target=FILTERED_HAM,
        save=True, conditions=[is_ham])
    def filter_ham(self):
        """
        Akismet detected this post as ham. Don't do anything (except change state).
        """
        pass

    @transition(
        field=state, source=[FILTERED_SPAM, MARKED_SPAM], target=MARKED_HAM,
        save=True)
    def mark_ham(self):
        """
        Either Akismet returned a false positive, or a moderator accidentally
        marked this as spam. Tell Akismet that this is ham, undelete it.
        """
        self._submit_ham()
        self._undelete_post()

    @transition(
        field=state, source=[FILTERED_HAM, MARKED_HAM], target=MARKED_SPAM,
        save=True)
    def mark_spam(self):
        """
        Akismet missed this, or a moderator accidentally marked it as ham. Tell
        Akismet that this is spam.
        """
        self._submit_spam()
        self._delete_post()

    def review(self, certainly_spam=False):
        """
        Process this post, used by the manager and the spam-hammer. The
        ``certainly_spam`` argument is used to force mark as spam/delete the
        post, no matter what status Akismet returns.
        """
        if can_proceed(self.filter_spam):
            self.filter_spam()
        elif can_proceed(self.filter_ham):
            self.filter_ham()
            if certainly_spam:
                post_status.mark_spam()
        else:
            if certainly_spam:
                self._delete_post()
            logger.warn("Couldn't filter post.", extra={'poststatus': self})


from .signals import post_saved, topic_saved

post_save.connect(post_saved, sender=Post, dispatch_uid='djangobb_post_save')
post_save.connect(topic_saved, sender=Topic, dispatch_uid='djangobb_topic_save')
