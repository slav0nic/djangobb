# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.auth.models import User

from djangobb_forum.models import Post, Reputation


class TestReputation(TestCase):
    fixtures = ['test_forum.json']
    
    def setUp(self):
        self.from_user = User.objects.get(pk=1)
        self.to_user = User.objects.get(pk=2)
        self.post = Post.objects.get(pk=1)
        self.reason = 'Test Reason'
    
    def test_reputation_plus(self):
        reputation = Reputation.objects.create(
            from_user=self.from_user, to_user=self.to_user, post=self.post,
            sign=1, reason=self.reason
        )
        reputations = Reputation.objects.filter(to_user__id=self.to_user.id)
        total_reputation = 0
        for reputation in reputations:
            total_reputation += reputation.sign
        self.assertEqual(total_reputation, 1)

    def test_reputation_minus(self):
        reputation = Reputation.objects.create(
            from_user=self.from_user, to_user=self.to_user, post=self.post,
            sign=-1, reason=self.reason
        )
        reputations = Reputation.objects.filter(to_user__id=self.to_user.id)
        total_reputation = 0
        for reputation in reputations:
            total_reputation += reputation.sign
        self.assertEqual(total_reputation, -1)