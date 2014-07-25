# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User, AnonymousUser
from django.test.utils import override_settings

from djangobb_forum.models import Post
from djangobb_forum.templatetags.forum_extras import profile_link, link, lofi_link, set_theme_style


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

    @override_settings(STATIC_URL='/static/')
    def test_set_theme_style(self):
        # Test for authenticated user
        self.user.forum_profile.theme = 'DjangoBB'
        style = set_theme_style(self.user)
        self.assertEqual(style, '<link rel="stylesheet" type="text/css" href="/static/djangobb_forum/themes/DjangoBB/style.css" />')

        # Test for anonymous
        style = set_theme_style(AnonymousUser())
        self.assertEqual(style, '<link rel="stylesheet" type="text/css" href="/static/djangobb_forum/themes/default/style.css" />')
