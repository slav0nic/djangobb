# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from djangobb_forum.models import Post
from djangobb_forum.templatetags.forum_extras import profile_link, link, lofi_link


class TestLinkTags(TestCase):
    fixtures = ['test_forum.json']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.post = Post.objects.get(pk=1)

    def test_profile_link(self):
        plink = profile_link(self.user)
        self.assertEqual(plink, "<a href=\"/forum/user/djangobb/\">djangobb</a>")

    def test_link(self):
        l = link(self.post)
        self.assertEqual(l, "<a href=\"/forum/post/1/\">Test Body</a>")

    def test_lofi_link(self):
        l = lofi_link(self.post)
        self.assertEqual(l, "<a href=\"/forum/post/1/lofi/\">Test Body</a>")
