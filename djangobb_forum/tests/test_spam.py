from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db import models
from django.template import Template, Context
from django.test import TestCase

from django_fsm.db.fields import can_proceed

from djangobb_forum import settings as forum_settings
from djangobb_forum.forms import AddPostForm
from djangobb_forum.models import Category, Forum, Topic, Post, PostStatus

profile_app, profile_model = settings.AUTH_PROFILE_MODULE.split('.')
UserProfileModel = models.get_model(profile_app, profile_model)

class ForumSpamTests(TestCase):
    multi_db = True
    
    def setUp(self):
        Category.objects.create(name=forum_settings.SPAM_CATEGORY_NAME)
        self.password = "password"
        self.user = User.objects.create_user(
            username="testuser", password=self.password)
        UserProfileModel.objects.create(user=self.user)
        new_scratchers = Group.objects.create(name="New Scratchers")
        self.user.groups.add(new_scratchers)
        self.veteran_user = User.objects.create_user(
            username="veteran_user", password=self.password)
        UserProfileModel.objects.create(user=self.veteran_user)
        self.moderator = User.objects.create_user(
            username="moderator", password=self.password)
        self.moderator.is_superuser = True
        self.moderator.save()
        UserProfileModel.objects.create(user=self.moderator)
        self.test_category = Category.objects.create(name="Test Category")
        self.test_forum = Forum.objects.create(
            name="Test Forum", category=self.test_category)
        self.test_topic = Topic.objects.create(
            name="Test Topic", forum=self.test_forum, user=self.user)
        self.test_post = Post.objects.create(
            topic=self.test_topic, user=self.user, body="Test content",
            body_html="<p>Test content</p>")
        User.objects.create_user(username="filterbot", password="password")
        User.objects.create_user(username="systemuser", password="password")

    # Model methods
    def test_get_spam_dustbin(self):
        """
        Ensure the dustbin forum and topic are created and available.
        """
        self.post_status = PostStatus.objects.create_for_post(self.test_post)
        topic, forum = self.post_status._get_spam_dustbin()
        self.assertTrue(topic is not None)
        self.assertTrue(forum is not None)

    def test_transition_filter_ham(self):
        """
        If a post is ham, it can transition to filtered as ham.
        """
        self.post_status = PostStatus.objects.create_for_post(self.test_post)
        self.post_status._comment_check = lambda: False
        self.post_status.is_ham = lambda: True
        self.post_status.is_spam = lambda: False
        self.assertTrue(can_proceed(self.post_status.filter_ham))
        self.post_status.filter_ham()
        self.assertEqual(PostStatus.FILTERED_HAM, self.post_status.state)

    def test_transition_filter_spam(self):
        """
        If a post is spam, it can transition to filtered as spam.
        """
        self.post_status = PostStatus.objects.create_for_post(self.test_post)
        self.post_status._comment_check = lambda: True
        self.post_status.is_ham = lambda: False
        self.post_status.is_spam = lambda: True
        self.assertTrue(can_proceed(self.post_status.filter_spam))
        self.post_status.filter_spam()
        self.assertEqual(PostStatus.FILTERED_SPAM, self.post_status.state)
        self.assertEqual(
            self.post_status.post.topic.forum.name, forum_settings.SPAM_FORUM_NAME)

    def test_transition_mark_ham(self):
        """
        Ensure a post filtered as spam can be marked as ham, and moved back to
        its original location after marking as ham.
        """
        self.post_status = PostStatus.objects.create_for_post(self.test_post)
        self.post_status.state = PostStatus.FILTERED_SPAM
        self.post_status.save()
        self.post_status._delete_post()
        self.post_status._submit_spam = lambda: True
        self.post_status._submit_ham = lambda: True
        self.assertTrue(can_proceed(self.post_status.mark_ham))
        self.post_status.mark_ham()
        self.assertEqual(PostStatus.MARKED_HAM, self.post_status.state)
        self.assertEqual(self.post_status.post.topic.name, "Test Topic")
        self.assertEqual(self.post_status.post.topic.forum.name, "Test Forum")

    def test_transition_mark_spam(self):
        """
        A post filtered as ham should be able to be marked as spam, and is moved
        to the spam forum/topic when marked.
        """
        self.post_status = PostStatus.objects.create_for_post(self.test_post)
        self.post_status.state = PostStatus.FILTERED_HAM
        self.post_status.save()
        self.post_status._submit_spam = lambda: True
        self.post_status._submit_ham = lambda: True
        self.assertTrue(can_proceed(self.post_status.mark_spam))
        self.post_status.mark_spam()
        self.assertEqual(PostStatus.MARKED_SPAM, self.post_status.state)
        self.assertEqual(
            self.post_status.post.topic.forum.name, forum_settings.SPAM_FORUM_NAME)

    def test_review_new_posts(self):
        ham_post = Post.objects.create(
            topic=self.test_topic, user=self.user, body="Test ham content",
            body_html="<p>Test ham content</p>")
        ham_post_status = PostStatus.objects.create_for_post(ham_post)
        ham_post_status._comment_check = lambda: False
        ham_post_status.is_ham = lambda: True
        ham_post_status.is_spam = lambda: False

        spam_post = Post.objects.create(
            topic=self.test_topic, user=self.user, body="Test spam content",
            body_html="<p>Test spam content</p>")
        spam_post_status = PostStatus.objects.create_for_post(spam_post)
        spam_post_status._comment_check = lambda: True
        spam_post_status.is_ham = lambda: False
        spam_post_status.is_spam = lambda: True

        unreviewed_post = Post.objects.create(
            topic=self.test_topic, user=self.user, body="Test unreviewed content",
            body_html="<p>Test unreviewed content</p>")
        unreviewed_post_status = PostStatus.objects.create_for_post(unreviewed_post)
        unreviewed_post_status._comment_check = lambda: None
        unreviewed_post_status.is_ham = lambda: False
        unreviewed_post_status.is_spam = lambda: False

        statuses = [ham_post_status, spam_post_status, unreviewed_post_status]

        oldfilter = PostStatus.objects.filter
        PostStatus.objects.filter = lambda state: statuses
        PostStatus.objects.review_new_posts()
        PostStatus.objects.filter = oldfilter
        self.assertEqual(
            1, PostStatus.objects.filter(state=PostStatus.UNREVIEWED).count())
        self.assertEqual(
            1, PostStatus.objects.filter(state=PostStatus.FILTERED_HAM).count())
        self.assertEqual(
            1, PostStatus.objects.filter(state=PostStatus.FILTERED_SPAM).count())


    # Template tags
    def test_can_proceed_tag(self):
        self.post_status = PostStatus.objects.create_for_post(self.test_post)
        self.post_status.state = PostStatus.FILTERED_HAM
        self.post_status.save()
        t = Template("{% load forum_extras %}{% if post_status|can_proceed:'mark_spam' %}Success{% else %}Failure{% endif %}")
        c = Context({'post_status': self.post_status})
        self.assertEqual("Success", t.render(c))
        t = Template("{% load forum_extras %}{% if post_status|can_proceed:'filter_spam' %}Failure{% else %}Success{% endif %}")
        self.assertEqual("Success", t.render(c))

    def test_in_group_tag(self):
        t = Template("{% load forum_extras %}{% if user|in_group:'New Scratchers' %}Success{% else %}Failure{% endif %}")
        c = Context({'user': self.user})
        self.assertEqual("Success", t.render(c))
        t = Template("{% load forum_extras %}{% if user|in_group:'New Scratchers' %}Failure{% else %}Success{% endif %}")
        c = Context({'user': self.moderator})
        self.assertEqual("Success", t.render(c))


    # Integration
    def test_status_created_topic(self):
        """
        Ensure a new scratcher's new topic generates an associated PostStatus.
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            reverse('djangobb:add_topic', args=[self.test_forum.id]),
            {
                'name': "test_status_created_topic",
                'body': "This is a test post, please ignore."})
        topic_query = Topic.objects.filter(name='test_status_created_topic')
        self.assertTrue(topic_query.exists())
        topic = topic_query.get()
        self.assertEqual(topic.posts.count(), 1)
        post = topic.last_post
        self.assertTrue(post.poststatus is not None)

    def test_status_created_post(self):
        """
        A new scratcher's reply should generate a PostStatus.
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(
            reverse('djangobb:topic', args=[self.test_topic.id]),
            {
                AddPostForm.FORM_NAME: True,
                'body': "Test test_status_created_post"})
        self.assertEqual(self.test_topic.posts.count(), 2)
        post = self.test_topic.posts.all()[1]
        self.assertTrue(post.poststatus is not None)
        self.client.logout()

    def test_status_not_created_not_new_scratcher_topic(self):
        """
        Ensure users who aren't new scratchers don't get PostStatus objects
        generated for their topics.
        """
        self.client.login(
            username=self.veteran_user.username, password=self.password)
        response = self.client.post(
            reverse('djangobb:add_topic', args=[self.test_forum.id]),
            {
                'name': "test_status_not_created_not_new_scratcher",
                'body': "This is a test post, please ignore."})
        post_query = Post.objects.filter(
            topic__name='test_status_not_created_not_new_scratcher')
        self.assertTrue(post_query.exists())
        post = post_query.get()
        with self.assertRaises(PostStatus.DoesNotExist):
            status = post.poststatus
        self.client.logout()

    def test_status_not_created_not_new_scratcher_post(self):
        """
        A non-new scratcher's reply should not generate a PostStatus.
        """
        self.client.login(
            username=self.veteran_user.username, password=self.password)
        response = self.client.post(
            reverse('djangobb:topic', args=[self.test_topic.id]),
            {
                AddPostForm.FORM_NAME: True,
                'body': "Test test_status_not_created_not_new_scratcher_post."})
        self.assertEqual(self.test_topic.posts.count(), 2)
        post = self.test_topic.posts.all()[1]
        with self.assertRaises(PostStatus.DoesNotExist):
            status = post.poststatus
        self.client.logout()

    def test_mod_can_see_spam_link_on_ham(self):
        """ Mods can see the "Mark as spam" link """
        self.client.login(
            username=self.moderator.username, password=self.password)
        ps = PostStatus.objects.create_for_post(self.test_post)
        ps.state = PostStatus.FILTERED_HAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id,]))
        self.assertContains(response, "postmarkspam")
        self.client.logout()

    def test_mod_can_see_ham_link_on_spam(self):
        """ Mods can see the "Un-mark as spam" link """
        self.client.login(
            username=self.moderator.username, password=self.password)
        ps = PostStatus.objects.create_for_post(self.test_post)
        ps.state = PostStatus.FILTERED_SPAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id,]))
        self.assertContains(response, "postmarkham")
        self.client.logout()

    def test_user_cannot_see_mark_links(self):
        """ Normal users can't see the "(Un-)Mark as spam" link """
        self.client.login(
            username=self.user.username, password=self.password)
        ps = PostStatus.objects.create_for_post(self.test_post)
        ps.state = PostStatus.FILTERED_SPAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id,]))
        self.assertNotContains(response, "postmarkham")
        self.assertNotContains(response, "postmarkspam")
        ps.state = PostStatus.FILTERED_HAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id,]))
        self.assertNotContains(response, "postmarkham")
        self.assertNotContains(response, "postmarkspam")
        self.client.logout()

    def test_mod_can_see_ban_link_new_scratcher(self):
        """ Mods can see the "Ban User" link on posts by New Scratchers """
        self.client.login(
            username=self.moderator.username, password=self.password)
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id]))
        link = reverse("ban_forum_spammer", args=[self.test_post.user.username])
        self.assertContains(response, link)
        self.client.logout()

    def test_mod_cannot_see_ban_link_normal_user(self):
        """ Mods don't see the "Ban User" link on posts by normal users """
        self.client.login(
            username=self.moderator.username, password=self.password)
        self.test_post.user = self.veteran_user
        self.test_post.save()
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id]))
        link = reverse("ban_forum_spammer", args=[self.test_post.user.username])
        self.assertNotContains(response, link)
        self.client.logout()

    def test_normal_user_can_never_see_ban_link(self):
        """ Normal users don't see the "Ban User" link on any posts """
        self.client.login(
            username=self.user.username, password=self.password)
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id]))
        link = reverse("ban_forum_spammer", args=[self.test_post.user.username])
        self.assertNotContains(response, link)
        self.test_post.user = self.veteran_user
        self.test_post.save()
        response = self.client.get(
            reverse("djangobb:topic", args=[self.test_post.topic.id]))
        link = reverse("ban_forum_spammer", args=[self.test_post.user.username])
        self.assertNotContains(response, link)
        self.client.logout()

    def test_mod_can_mark_spam(self):
        """ Mods can mark posts as spam and it changes the state of the post """
        self.client.login(
            username=self.moderator.username, password=self.password)
        ps = PostStatus.objects.create_for_post(self.test_post)
        ps.state = PostStatus.FILTERED_HAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:mark_post_spam", args=[self.test_post.id,]))
        self.assertEqual(self.test_post.poststatus.state, PostStatus.MARKED_SPAM)
        self.client.logout()

    def test_mod_can_mark_ham(self):
        """ Mods can mark posts as ham and it changes the state of the post """
        self.client.login(
            username=self.moderator.username, password=self.password)
        ps = PostStatus.objects.create_for_post(self.test_post)
        ps.state = PostStatus.FILTERED_SPAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:mark_post_ham", args=[self.test_post.id,]))
        self.assertEqual(self.test_post.poststatus.state, PostStatus.MARKED_HAM)
        self.client.logout()

    def test_normal_user_cannot_mark(self):
        """
        Normal users are forbidden from marking as spam/ham and it does not
        affect the state of the post.
        """
        self.client.login(
            username=self.user.username, password=self.password)
        ps = PostStatus.objects.create_for_post(self.test_post)
        ps.state = PostStatus.FILTERED_HAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:mark_post_spam", args=[self.test_post.id,]))
        self.assertEqual(self.test_post.poststatus.state, PostStatus.FILTERED_HAM)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            reverse("djangobb:mark_post_ham", args=[self.test_post.id,]))
        self.assertEqual(PostStatus.objects.get(post=self.test_post).state, PostStatus.FILTERED_HAM)
        self.assertEqual(response.status_code, 403)
        ps.state = PostStatus.FILTERED_SPAM
        ps.save()
        response = self.client.get(
            reverse("djangobb:mark_post_spam", args=[self.test_post.id,]))
        self.assertEqual(PostStatus.objects.get(post=self.test_post).state, PostStatus.FILTERED_SPAM)
        self.assertEqual(response.status_code, 403)
        response = self.client.get(
            reverse("djangobb:mark_post_ham", args=[self.test_post.id,]))
        self.assertEqual(PostStatus.objects.get(post=self.test_post).state, PostStatus.FILTERED_SPAM)
        self.assertEqual(response.status_code, 403)
        self.client.logout()
