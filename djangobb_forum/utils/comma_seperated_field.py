# coding:utf-8

"""
    code based on:
    https://github.com/jedie/django-tools/blob/master/django_tools/fields/sign_separated.py
"""

import warnings

if __name__ == "__main__":
    # For running doctest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django import forms
from django.db import models
from django.conf import settings


def _join(values):
    if isinstance(values, list):
        value = ",".join([str(i) for i in values])
        return value

def _split(value):
    if isinstance(value, basestring):
        try:
            value = [int(i) for i in value.split(",")]
        except ValueError, err:
            # e.g.: old JSONField data
            if settings.DEBUG:
                warnings.warn("ValueError: %s" % err)
            return None
    return value


class CommaSeparatedInput(forms.widgets.Input):
    input_type = 'text'
    def render(self, name, value, attrs=None):
        value = _join(value)
        return super(CommaSeparatedInput, self).render(name, value, attrs)


class CommaSeparatedFormField(forms.CharField):
    widget = CommaSeparatedInput
    def to_python(self, value):
        return _split(value)


class CommaSeperatedIntegersField(models.TextField):
    """
    >>> CommaSeperatedIntegersField().to_python("1,2,3")
    [1, 2, 3]
    
    >>> CommaSeperatedIntegersField().get_prep_value([1,2,3])
    '1,2,3'
    
    >>> f = CommaSeperatedIntegersField().formfield()
    >>> f.clean(u"1,2,3,4")
    [1, 2, 3, 4]
    
    # No valid data would be cleared:
    >>> f = CommaSeperatedIntegersField().formfield()
    >>> f.clean(u"1,2,a,b")
    Traceback (most recent call last):
    ...
    ValidationError: [u'This field is required.']
      
    >>> from django.db import models
    >>> from django.forms.models import ModelForm
        
    >>> class TestModel(models.Model):
    ...     test = CommaSeperatedIntegersField()
    ...     class Meta:
    ...         app_label = "django_tools"
    
    >>> class TestForm(ModelForm):
    ...     class Meta:
    ...         model = TestModel
    
    >>> f = TestForm({'test': None})
    >>> f.is_valid()
    False
    >>> f = TestForm({'test': ""})
    >>> f.is_valid()
    False
    >>> f = TestForm({'test': "1,2,3"})
    >>> f.is_valid()
    True
    >>> f.cleaned_data
    {'test': [1, 2, 3]}
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        return _split(value)

    def get_prep_value(self, value, *args, **kwargs):
        return _join(value)

    def formfield(self, **kwargs):
        """ Use always own widget and form field. """
        kwargs["widget"] = CommaSeparatedInput
        kwargs["form_class"] = CommaSeparatedFormField
        return super(CommaSeperatedIntegersField, self).formfield(**kwargs)


if __name__ == "__main__":
    # Run all unittest directly
    import doctest
    print doctest.testmod()
