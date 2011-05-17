# -*- coding: utf-8 -*-
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User

from djangobb_forum.models import Post
from djangobb_forum.util import urlize, smiles, convert_text_to_html, paginate, set_language\
     

class TestParsers(TestCase):
    def setUp(self):
        self.data_url = "Lorem ipsum dolor sit amet, consectetur http://djangobb.org/ adipiscing elit."
        self.data_smiles = "Lorem ipsum dolor :| sit amet :) <a href=\"http://djangobb.org/\">http://djangobb.org/</a>"
        self.markdown = ""
        self.bbcode = "[b]Lorem[/b] [code]ipsum :)[/code] =)"

    def test_urlize(self):
        urlized_data = urlize(self.data_url)
        self.assertEqual(urlized_data, u"Lorem ipsum dolor sit amet, consectetur <a href=\"http://djangobb.org/\" rel=\"nofollow\">http://djangobb.org/</a> adipiscing elit.")

    def test_smiles(self):
        smiled_data = smiles(self.data_smiles)
        self.assertEqual(smiled_data, u"Lorem ipsum dolor <img src=\"/static/forum/img/smilies/neutral.png\" /> sit amet <img src=\"/static/forum/img/smilies/smile.png\" /> <a href=\"http://djangobb.org/\">http://djangobb.org/</a>")
    
    def test_convert_text_to_html(self):
        bb_data = convert_text_to_html(self.bbcode, 'bbcode')
        self.assertEqual(bb_data, "<strong>Lorem</strong> <div class=\"code\"><pre>ipsum :)</pre></div>=)")

class TestPaginators(TestCase):
    fixtures = ['test_forum.json']

    def setUp(self):
        self.posts = Post.objects.all()[:5]
        self.factory = RequestFactory()

    def test_paginate(self):
        request = self.factory.get('/?page=2')
        pages, paginator, _ = paginate(self.posts, request, 3)
        self.assertEqual(pages, 2)

        request = self.factory.get('/?page=1')
        _, _, paged_list_name = paginate(self.posts, request, 3)
        self.assertEqual(paged_list_name.count(), 3)
