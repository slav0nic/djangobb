# -*- coding: utf-8 -*-
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from djangobb_forum.models import Category, Forum, Topic, Post


class TestForum(TestCase):
    fixtures = ['test_forum.json']

    def setUp(self):
        self.category = Category.objects.get(pk=1)
        self.forum = Forum.objects.get(pk=1)
        self.topic = Topic.objects.get(pk=1)
        self.post = Post.objects.get(pk=1)
        self.user = User.objects.get(pk=1)
        self.client = Client()
        self.client.login(username='djangobb', password='djangobb')

    def test_index_authericated_view(self):
        response = self.client.get(reverse('djangobb:index'))
        self.assertEqual(response.status_code, 200)

    def test_forum_view(self):
        response = self.client.get(reverse('djangobb:forum', kwargs={'forum_id':
                                                            self.forum.pk}))
        self.assertEqual(response.status_code, 200)

    def test_topic_view(self):
        response = self.client.get(reverse('djangobb:topic', kwargs={'topic_id':
                                                            self.topic.pk}))
        self.assertEqual(response.status_code, 200)

    def test_create_topic(self):
        response = self.client.post(reverse('djangobb:add_topic', kwargs={'forum_id':
                                                            self.forum.pk}),
                                                            {'name': 'title',
                                                            'body': 'topic body'
                                                            }
                                    )
        topic = Topic.objects.filter(forum=self.forum).latest()
        post_url = reverse('djangobb:post',
                            kwargs={'post_id': topic.last_post.pk})

        self.assertRedirects(response, post_url, target_status_code=302)

        response = self.client.get(post_url)
        topic_url = reverse('djangobb:topic', kwargs={'topic_id': topic.pk})
        self.assertIn(topic_url, response.url)
