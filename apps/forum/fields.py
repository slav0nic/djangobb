"""
Details about AutoOneToOneField:
    http://softwaremaniacs.org/blog/2007/03/07/auto-one-to-one-field/
"""
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import logging
try:
    import cPickle as pickle
except ImportError:
    import Pickle as pickle

from django.db.models import OneToOneField
from django.db.models.fields.related import SingleRelatedObjectDescriptor 
from django.db import models
from django.core.files.uploadedfile import SimpleUploadedFile


class AutoSingleRelatedObjectDescriptor(SingleRelatedObjectDescriptor):
    def __get__(self, instance, instance_type=None):
        try:
            return super(AutoSingleRelatedObjectDescriptor, self).__get__(instance, instance_type)
        except self.related.model.DoesNotExist:
            obj = self.related.model(**{self.related.field.name: instance})
            obj.save()
            return obj


class AutoOneToOneField(OneToOneField):
    """
    OneToOneField creates dependent object on first request from parent object
    if dependent oject has not created yet.
    """

    def contribute_to_related_class(self, cls, related):
        setattr(cls, related.get_accessor_name(), AutoSingleRelatedObjectDescriptor(related))
        #if not cls._meta.one_to_one_field:
        #    cls._meta.one_to_one_field = self


class ExtendedImageField(models.ImageField):
    """
    Extended ImageField that can resize image before saving it.
    """

    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop('width', None)
        self.height = kwargs.pop('height', None)
        super(ExtendedImageField, self).__init__(*args, **kwargs)

    def save_form_data(self, instance, data):
        if data and self.width and self.height:
            content = self.resize_image(data.read(), width=self.width, height=self.height)
            data = SimpleUploadedFile(data.name, content, data.content_type)
        super(ExtendedImageField, self).save_form_data(instance, data)

    def resize_image(self, rawdata, width, height):
        """
        Resize image to fit it into (width, height) box.
        """
        try:
            import Image
        except ImportError:
            from PIL import Image
        image = Image.open(StringIO(rawdata))
        try:
            oldw, oldh = image.size
            if oldw >= oldh:
                x = int(round((oldw - oldh) / 2.0))
                image = image.crop((x, 0, (x + oldh) - 1, oldh - 1))
            else:
                y = int(round((oldh - oldw) / 2.0))
                image = image.crop((0, y, oldw - 1, (y + oldw) - 1))
            image = image.resize((width, height), resample=Image.ANTIALIAS)
        except Exception, err:
            logging.error(err)
            return ''

        string = StringIO()
        image.save(string, format='PNG')
        return string.getvalue()


class RangesField(models.TextField):
    """
    Field for stored pickled data.
    Taken from Cicero forum engine.
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, list):
            return value
        if not value:
            return [(0, 0)]
        return pickle.loads(str(value))

    def get_db_prep_value(self, value):
        return unicode(pickle.dumps(value))
