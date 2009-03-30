from datetime import datetime, timedelta
import pickle
import cgi

from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import Client
from django.conf.urls.defaults import *
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import login, authenticate

from account.auth_key import strftime, strptime,\
    generate_key, wrap_url, validate_key

class AccountTestCase(TestCase):
    urls = 'account.tests'

    def setUp(self):
        User.objects.all().delete()
        u = User(username='user', email='user@host.com')
        u.set_password('pass')
        u.is_active = True
        u.save()
        self.user = u

        u = User(username='ban_user', email='ban_user@host.com')
        u.set_password('pass')
        u.is_active = False
        u.save()
        self.ban_user = u
        
        # New email
        expired = datetime.now() + timedelta(days=1)
        url, args = process_url(test_url, username=self.user.username, expired=expired,
                                action='new_email', email='user_gaz@host.com')
        self.assertEqual('user@host.com', self.user.email)
        resp = self.client.get(url, args)
        self.assertEqual(self.client.session['_auth_user_id'], self.user.id)
        user = User.objects.get(pk=self.user.id)
        self.assertEqual(user.email, 'user_gaz@host.com')


class AuthCodeTestCase(AccountTestCase):
    def test_generate_key(self):
        # should not fail
        generate_key(username=self.user.username, expired=datetime.now())


    def test_wrap_url(self):
        expired = datetime.now()
        key, b64 = generate_key(username=self.user.username, expired=expired)

        link = 'http://ya.ru'
        self.assertEqual(wrap_url(link, username=self.user.username, expired=expired),
                         '%s?authkey=%s' % (link, b64))

        link = 'http://ya.ru?foo=bar'
        self.assertEqual(wrap_url(link, username=self.user.username, expired=expired),
                         '%s&authkey=%s' % (link, b64))


    def test_validate_key(self):
        expired = datetime.now() - timedelta(seconds=1)
        key, b64 = generate_key(username=self.user.username, expired=expired)
        self.assertFalse(validate_key(b64))

        expired = datetime.now() + timedelta(seconds=10)
        key, b64 = generate_key(username=self.user.username, expired=expired)
        self.assertTrue(validate_key(b64))

        key, b64 = generate_key(username=self.user.username, expired='asdf')
        self.assertFalse(validate_key(b64))


class AuthKeyMiddlewareTestCase(AccountTestCase):

    def testActivation(self): 
        def process_url(url, **kwargs):
           url = wrap_url(url, **kwargs)
           return url.split('?')[0], cgi.parse_qs(url.split('?')[1])

        test_url = '/account_test_view/'
        expired = datetime.now() + timedelta(days=1)
        resp = self.client.get(test_url)

        # Guest has no cookies
        self.assertFalse(self.client.cookies)

        # Simple authorization
        url, args = process_url(test_url, username=self.user.username, expired=expired)
        resp = self.client.get(url, args)
        self.assertEqual(self.client.session['_auth_user_id'], self.user.id)
        self.client.session.flush()

        # Baned user can't authorize
        url, args = process_url(test_url, username=self.ban_user.username, expired=expired)
        resp = self.client.get(url, args)
        self.assert_('_auth_user_id' not in self.client.session)
        self.client.session.flush()

        # Activation of baned user
        url, args = process_url(test_url, username=self.ban_user.username, expired=expired, action='activation')
        resp = self.client.get(url, args)
        self.assertEqual(self.client.session['_auth_user_id'], self.ban_user.id)
        self.client.session.flush()

        # New password
        url, args = process_url(test_url, username=self.user.username, expired=expired,
                                action='new_password', password='foobar')
        self.assertTrue(authenticate(username=self.user.username, password='pass'))
        resp = self.client.get(url, args)
        self.assertEqual(self.client.session['_auth_user_id'], self.user.id)
        self.client.session.flush()
        self.assertTrue(authenticate(username=self.user.username, password='foobar'))
        self.client.session.flush()

        # Expired auth key do not work
        expired = datetime.now() - timedelta(seconds=1)
        url, args = process_url(url, username=self.user.username, expired=expired)
        resp = self.client.get(url, args)
        self.assert_('_auth_user_id' not in self.client.session)


def test_view(request):
    return HttpResponse(request.user and request.user.username or '')

urlpatterns = patterns('',
    url('account_test_view/', test_view, name='account_test_view'),
)
