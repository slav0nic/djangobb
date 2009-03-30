from django.db import models
from captcha.conf import settings as captcha_settings
import datetime, sha


class CaptchaStore(models.Model):
    challenge = models.CharField(blank=False, max_length=32)
    response = models.CharField(blank=False, max_length=32)
    hashkey = models.CharField(blank=False, max_length=40,unique=True)
    expiration = models.DateTimeField(blank=False)
    
    def save(self,force_insert=False,force_update=False):
        self.response = self.response.lower()
        if not self.expiration:
            self.expiration = datetime.datetime.now() + datetime.timedelta(minutes= int(captcha_settings.CAPTCHA_TIMEOUT))
        if not self.hashkey:
            self.hashkey = sha.new(str(self.challenge) + str(self.response)).hexdigest()
        super(CaptchaStore,self).save(force_insert=force_insert,force_update=force_update)

    def __unicode__(self):
        return self.challenge

    @classmethod
    def remove_expired(cls):
        cls.objects.filter(expiration__lte=datetime.datetime.now()).delete()
    