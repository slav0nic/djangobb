from captcha.models import CaptchaStore
from captcha.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
import datetime


class CaptchaCase(TestCase):
    urls = 'captcha.tests.urls'

    def setUp(self):
        self.default_challenge = settings.get_challenge()()
        self.math_challenge = settings._callable_from_string('captcha.helpers.math_challenge')()
        self.chars_challenge = settings._callable_from_string('captcha.helpers.random_char_challenge')()
        
        self.default_store, created =  CaptchaStore.objects.get_or_create(challenge=self.default_challenge[0],response=self.default_challenge[1])
        self.math_store, created = CaptchaStore.objects.get_or_create(challenge=self.math_challenge[0],response=self.math_challenge[1])
        self.chars_store, created = CaptchaStore.objects.get_or_create(challenge=self.chars_challenge[0],response=self.chars_challenge[1])

    def testImages(self):
        for key in (self.math_store.hashkey, self.chars_store.hashkey, self.default_store.hashkey):
            response = self.client.get(reverse('captcha-image',kwargs=dict(key=key)))
            self.failUnlessEqual(response.status_code, 200)
            self.assertTrue(response.has_header('content-type'))
            self.assertEquals(response._headers.get('content-type'), ('Content-Type', 'image/png'))

    def testAudio(self):
        if not settings.CAPTCHA_FLITE_PATH:
            return
        for key in (self.math_store.hashkey, self.chars_store.hashkey, self.default_store.hashkey):
            response = self.client.get(reverse('captcha-audio',kwargs=dict(key=key)))
            self.failUnlessEqual(response.status_code, 200)
            self.assertTrue(len(response.content) > 1024)
            self.assertTrue(response.has_header('content-type'))
            self.assertEquals(response._headers.get('content-type'), ('Content-Type', 'audio/x-wav'))
            
    def testFormSubmit(self):        
        r = self.client.get(reverse('captcha-test'))
        self.failUnlessEqual(r.status_code, 200)
        hash_ = r.content[r.content.find('value="')+7:r.content.find('value="')+47]
        try:
            response = CaptchaStore.objects.get(hashkey=hash_).response
        except:
            self.fail()
            
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_,captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.failUnlessEqual(r.status_code, 200)
        self.assertTrue(r.content.find('Form validated') > 0)
        
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_,captcha_1=response, subject='xxx', sender='asasd@asdasd.com'))
        self.failUnlessEqual(r.status_code, 200)
        self.assertFalse(r.content.find('Form validated') > 0)

    def testWrongSubmit(self):        
        r = self.client.get(reverse('captcha-test'))
        self.failUnlessEqual(r.status_code, 200)
        r = self.client.post(reverse('captcha-test'), dict(captcha_0='abc',captcha_1='wrong response', subject='xxx', sender='asasd@asdasd.com'))
        self.assertFormError(r,'form','captcha','Error')

    def testDeleteExpired(self):
        self.default_store.expiration = datetime.datetime.now() - datetime.timedelta(minutes=5)
        self.default_store.save()
        hash_ = self.default_store.hashkey
        r = self.client.post(reverse('captcha-test'), dict(captcha_0=hash_,captcha_1=self.default_store.response, subject='xxx', sender='asasd@asdasd.com'))
        
        self.failUnlessEqual(r.status_code, 200)
        self.assertFalse(r.content.find('Form validated') > 0)
        
        # expired -> deleted
        try:
            CaptchaStore.objects.get(hashkey=hash_)
            self.fail()
        except:
            pass
