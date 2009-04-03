# -*- coding: utf-8
import re

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext as _
from django.template import loader

from forum.models import Profile
from forum.models import TZ_CHOICES, PRIVACY_CHOICES
from django.conf import settings

ACCOUNT_CAPTCHA = getattr(settings, 'ACCOUNT_CAPTCHA', False)

if ACCOUNT_CAPTCHA:
    from captcha.fields import CaptchaField

RE_USERNAME = getattr(settings, 'ACCOUNT_RE_USERNAME',
                      re.compile(r'[a-z0-9][_a-z0-9]*[a-z0-9]$', re.I))
USERNAME_MIN_LENGTH = getattr(settings, 'ACCOUNT_USERNAME_MIN_LENGTH', 3)
USERNAME_MAX_LENGTH = getattr(settings, 'ACCOUNT_USERNAME_MAX_LENGTH', 20)

PASSWORD_MIN_LENGTH = getattr(settings, 'ACCOUNT_PASSWORD_MIN_LENGTH', 5)
PASSWORD_MAX_LENGTH = getattr(settings, 'ACCOUNT_PASSWORD_MAX_LENGTH', 15)

class UsernameField(forms.CharField):
    """
    Form field for username handling.
    """

    def __init__(self, *args, **kwargs):
        super(UsernameField, self).__init__(*args, **kwargs)
        self.label = _(u'Username')
        self.help_text = _(u'You can use a-z, 0-9 and underscore. Login length should be between %d and %d' % (USERNAME_MIN_LENGTH, USERNAME_MAX_LENGTH))


    def clean(self, value):
        super(UsernameField, self).clean(value)

        if len(value) < USERNAME_MIN_LENGTH:
            raise forms.ValidationError(_(u'Login length is less than %d' % USERNAME_MIN_LENGTH))
        if len(value) > USERNAME_MAX_LENGTH:
            raise forms.ValidationError(_(u'Login length is more than %d' % USERNAME_MAX_LENGTH))
        if not RE_USERNAME.match(value):
            raise forms.ValidationError(_(u'Login contains restricted symbols'))

        try:
            User.objects.get(username__exact=value)
        except User.DoesNotExist:
            return value
        else:
            raise forms.ValidationError(_(u'This login already registered'))


class PasswordField(forms.CharField):
    """
    Form field for password handling.
    """

    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(*args, **kwargs)
        self.widget = forms.PasswordInput()
        self.help_text = ''


    def clean(self, value):
        super(PasswordField, self).clean(value)
        if len(value) < PASSWORD_MIN_LENGTH:
            raise forms.ValidationError(_(u'Password length is less than %d' % PASSWORD_MIN_LENGTH))
        if len(value) > PASSWORD_MAX_LENGTH:
            raise forms.ValidationError(_(u'Password length is more than %d' % PASSWORD_MAX_LENGTH))
        return value


class RegistrationForm(forms.Form):
    username = UsernameField()
    email = forms.EmailField(label=_('Email'))
    password = PasswordField(label=_('Password'))
    password_dup = PasswordField(label=_('Confirm password'))
    time_zone = forms.ChoiceField(label=_('Time zone'), choices=TZ_CHOICES)
    privacy_permission = forms.ChoiceField(label=_('Privacy permission'), choices=PRIVACY_CHOICES)

    def __init__(self, *args, **kwargs):
        self.base_fields['privacy_permission'].widget = forms.RadioSelect(  
                                                    choices=self.base_fields['privacy_permission'].choices
                                                    )
        super(RegistrationForm, self).__init__(*args, **kwargs)
        if ACCOUNT_CAPTCHA:
            self.fields['captcha'] = CaptchaField()

    
    def clean_email(self):
        #return self.cleaned_data.get('email','')
        try:
            User.objects.get(email__exact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        except KeyError:
            pass
        else:
            raise forms.ValidationError(_(u'This email already registered'))

    
    def clean(self):
        pwd1 = self.cleaned_data.get('password')
        pwd2 = self.cleaned_data.get('password_dup')
        if pwd1 and pwd2:
            if pwd1 != pwd2:
                # show error on top of password_dup field
                self._errors['password_dup'] = [_('Passwords do not match')]
        return self.cleaned_data


    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        time_zone = self.cleaned_data['time_zone']
        privacy_permission = self.cleaned_data['privacy_permission']
        user = User.objects.create_user(username, email, password=password)
        user.save()
        profile = Profile(user = user,
                              time_zone = time_zone,
                              privacy_permission = privacy_permission,
                              status = 'Member'
                             )
        profile.save()
        return user


class RestorePasswordForm(forms.Form):
    email = forms.EmailField(label=_('Email'))

    def clean_email(self):
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email']
            if User.objects.filter(email=email).count():
                return email
            else:
                raise forms.ValidationError(_(u'This email is not registered'))


class LoginForm(forms.Form):
    username = forms.CharField(label=_('Username'))
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        self.base_fields['username'].help_text = ''
        self.base_fields['password'].help_text = ''
        super(LoginForm, self).__init__(*args, **kwargs)


    def clean(self):
        super(LoginForm, self).clean()
        if self.is_valid():
            user = authenticate(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'])
            if not user is None:
                if user.is_active:
                    login(self.request, user)
                    return self.cleaned_data
                else:
                    raise forms.ValidationError(_(u'Sorry. You account is not active. Maybe you didn\'t activate it.'))
            else:
                raise forms.ValidationError(_(u'Incorrect login or password'))


class NewPasswordForm(forms.Form):
    """
    Form for changing user's password.
    """

    old_password = PasswordField(label=_(u'Old password'))
    password = PasswordField(label=_(u'Password'))
    password_confirmation = PasswordField(label=_(u'Password (confirmation)'))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        if not self.user.has_usable_password():
            self.base_fields['old_password'] = forms.Field(widget=forms.HiddenInput, required=False)
        super(NewPasswordForm, self).__init__(*args, **kwargs)


    def clean_old_password(self):
        password = self.cleaned_data['old_password']
        if password:
            test_user = authenticate(username=self.user.username,
                                     password=password)
            if test_user:
                return password
            else:
                raise forms.ValidationError(_('Incorrect old password'))


    def clean_password_confirmation(self):
        pass1 = self.cleaned_data['password']
        pass2 = self.cleaned_data['password_confirmation']
        if pass1 != pass2:
            raise forms.ValidationError(_(u'The passwords do not match'))
        else:
            return pass1


    def save(self):
        self.user.set_password(self.cleaned_data['password'])
        self.user.save()
        return self.user
    
class NewEmailForm(forms.Form):
      """
      Form for email chanage.
      """
      
      email = forms.EmailField(label=_(u'New email'))
      
      def save(self):
          pass
