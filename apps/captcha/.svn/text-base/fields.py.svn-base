from django.forms.fields import CharField, MultiValueField
from django.forms import ValidationError
from django.forms.widgets import TextInput, MultiWidget, HiddenInput
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from captcha.models import CaptchaStore
from captcha.conf import settings
from captcha.helpers import *
import datetime

class CaptchaTextInput(MultiWidget):
    def __init__(self,attrs=None):
        widgets = (
            HiddenInput(attrs),
            TextInput(attrs),
        )
        super(CaptchaTextInput,self).__init__(widgets,attrs)
    
    def decompress(self,value):
        if value:
            return value.split(',')
        return [None,None]
        
    def render(self, name, value, attrs=None):
        challenge,response= settings.get_challenge()()
        
        store, created = CaptchaStore.objects.get_or_create(challenge=challenge,response=response)
        key = store.hashkey
        value = [key, u'']
        
        ret = '<img src="%s" alt="captcha" class="captcha" />' %reverse('captcha-image',kwargs=dict(key=key))
        if settings.CAPTCHA_FLITE_PATH:
            ret = '<a href="%s" title="%s">%s</a>' %( reverse('captcha-audio', kwargs=dict(key=key)), unicode(_('Play captcha as audio file')), ret)
        return mark_safe(ret + super(CaptchaTextInput, self).render(name, value, attrs=attrs))

class CaptchaField(MultiValueField):
    widget=CaptchaTextInput
    
    def __init__(self, *args,**kwargs):
        fields = (
            CharField(show_hidden_initial=True), 
            CharField(),
        )
        super(CaptchaField,self).__init__(fields=fields, *args, **kwargs)
    
    def compress(self,data_list):
        if data_list:
            return ','.join(data_list)
        return None
        
    def clean(self, value):
        super(CaptchaField, self).clean(value)
        response, value[1] = value[1].strip().lower(), ''
        CaptchaStore.remove_expired()
        try:
            store = CaptchaStore.objects.get(response=response,hashkey=value[0], expiration__gt=datetime.datetime.now())
            store.delete()
        except Exception:
            raise ValidationError('Error')
        return value
