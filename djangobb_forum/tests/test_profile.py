# -*- coding: utf-8 -*-
from django.test import TestCase

from djangobb_forum.models import Profile


class TestProfile(TestCase):
    fixtures = ['test_forum.json']
    
    def setUp(self):
        self.profile = Profile.objects.get(pk=1)
        self.signature = 'Test Signature'
        self.jabber = 'Test Jabber'
        self.icq = 'Test ICQ'
        self.msn = 'Test MSN'
        self.aim = 'Test AIM'
        self.yahoo = 'Test YAHOO'
        self.status = 'Test Status'
        self.location = 'Test Location'
        self.site = 'http://djangobb.org/'
        
    def test_personal_profile(self):
        self.profile.status = self.status
        self.assertEqual(self.profile.status, self.status)
        self.profile.location = self.location
        self.assertEqual(self.profile.location, self.location)
        self.profile.site = self.site
        self.assertEqual(self.profile.site, self.site)
        
    def test_messaging_profile(self):
        self.profile.jabber = self.jabber
        self.assertEqual(self.profile.jabber, self.jabber)
        self.profile.icq = self.icq
        self.assertEqual(self.profile.icq, self.icq)
        self.profile.msn = self.msn
        self.assertEqual(self.profile.msn, self.msn)
        self.profile.aim = self.aim
        self.assertEqual(self.profile.aim, self.aim)
        self.profile.yahoo = self.yahoo
        self.assertEqual(self.profile.yahoo, self.yahoo)
        
    def test_personality_profile(self):
        self.profile.show_avatar = False
        self.assertEqual(self.profile.show_avatar, False)
        self.profile.signature = self.signature
        self.assertEqual(self.profile.signature, self.signature)
        
    def test_display_profile(self):
        self.profile.show_smilies = False
        self.assertEqual(self.profile.show_smilies, False)
        
    def test_privacy_profile(self):
        self.profile.privacy_permission = 0 
        self.assertEqual(self.profile.privacy_permission, 0)