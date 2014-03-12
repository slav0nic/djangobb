from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.db import models
from django.test import TestCase

from django_fsm.db.fields import can_proceed

from djangobb_forum import settings as forum_settings
from djangobb_forum.forms import AddPostForm
from djangobb_forum.models import Category, Forum, Topic, Post, PostStatus

profile_app, profile_model = settings.AUTH_PROFILE_MODULE.split('.')
UserProfileModel = models.get_model(profile_app, profile_model)

class BaseTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name=forum_settings.SPAM_CATEGORY_NAME)
        self.password = "password"
        self.user = User.objects.create_user(
            username="testuser", password=self.password)
        UserProfileModel.objects.create(user=self.user)
        new_scratchers = Group.objects.create(name="New Scratchers")
        self.user.groups.add(new_scratchers)
        self.veteran_user = User.objects.create_user(
            username="veteranuser", password=self.password)
        UserProfileModel.objects.create(user=self.veteran_user)
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


class TestPostStatusUnit(BaseTestCase):
    def setUp(self):
        super(TestPostStatusUnit, self).setUp()

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


class TestPostStatusIntegration(BaseTestCase):        
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
