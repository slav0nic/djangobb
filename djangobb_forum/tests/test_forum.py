# -*- coding: utf-8 -*-
from django.test import TestCase, Client
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
        self.ip = '127.0.0.1'
        
    def test_login(self):
        self.assertTrue(self.client.login(username='djangobb', password='djangobb'))
    
    def test_create_topic(self):
        topic = Topic.objects.create(forum=self.forum, user=self.user, name="Test Title")
        self.assert_(topic)
        post = Post.objects.create(
            topic=topic, user=self.user, user_ip=self.ip,
            markup='bbcode', body='Test Body'
        )
        self.assert_(post)
        
    def test_create_post(self):
        post = Post.objects.create(
            topic=self.topic, user=self.user, user_ip=self.ip,
            markup='bbcode', body='Test Body'
        )
        self.assert_(post)
        
    def test_edit_post(self):
        self.post.body = 'Test Edit Body'
        self.assertEqual(self.post.body, 'Test Edit Body')