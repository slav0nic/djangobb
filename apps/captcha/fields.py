# Original: http://django-pantheon.googlecode.com/svn/trunk/pantheon/supernovaforms/

from django import forms

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from apps.captcha import util

class ImageWidget( forms.Widget ):
    """
    Widget for rendering captcha image.
    """

    def render( self, name, value, attrs=None ):
        return forms.HiddenInput().render( name, value ) + u'<img src="%s"/> ' % value


class CaptchaWidget( forms.MultiWidget ):
    """
    Multiwidget for rendering captcha field.
    """

    def __init__(self, attrs = None):
        widgets = ( forms.HiddenInput(), ImageWidget(), forms.TextInput())
        super( CaptchaWidget, self ).__init__( widgets, attrs )
   

    def format_output(self, widgets):
        return u'<div class="captcha">%s<div class="captcha-image">%s</div><div class="captcha-input">%s</div></div>' % (widgets[0], widgets[1], widgets[2])
   

    def decompress(self, value):
        captcha_id = util.generate_captcha()
        url = reverse('apps.captcha.views.captcha_image', args=[captcha_id])
        return (captcha_id, url, '')


    def render(self, name, value, attrs=None):
        # None value forces call to decompress
        # which will generate new captcha
        return super(CaptchaWidget, self).render(name, None, attrs)
   

class CaptchaField(forms.Field):
    """
    Captcha field.
    """

    widget = CaptchaWidget

    def __init__(self, *args, **kwargs):
        super(CaptchaField, self).__init__(*args, **kwargs)
        self.label = _('Human test')
        self.help_text = _('Please, enter the word on the picture')


    def clean(self, values):
        """
        Test the solution
        
        If succes delete the solution.
        """
        
        id, url, solution = values
        if not util.test_solution(id, solution):
            raise forms.ValidationError(_('Incorrect answer'))
        else:
            util.delete_solution(id)
            return values
