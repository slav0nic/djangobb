from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from datetime import datetime

from djapian import utils

class ChangeManager(models.Manager):
    def create(self, object, action, **kwargs):
        ct = ContentType.objects.get_for_model(object.__class__)

        try:
            old_change = self.get(
                content_type=ct,
                object_id=object.pk
            )
            if old_change.action=="add":
                if action=="edit":
                    old_change.save()
                    return old_change
                elif action=="delete":
                    old_change.delete()
                    return None
            old_change.delete()
        except self.model.DoesNotExist:
            old_change = self.model(object=object)

        old_change.action = action
        old_change.save()

        return old_change


class Change(models.Model):
    ACTIOINS = (
        ("add", "object added"),
        ("edit", "object edited"),
        ("delete", "object deleted"),
    )

    content_type = models.ForeignKey(ContentType, db_index=True)
    object_id = models.PositiveIntegerField()
    date = models.DateTimeField(default=datetime.now)
    action = models.CharField(max_length=6, choices=ACTIOINS)

    object = generic.GenericForeignKey()

    objects = ChangeManager()

    def __unicode__(self):
        return u'%s#%d To action:`%s`, added on %s' % (
            self.content_type,
            self.object_id,
            self.action,
            self.date
        )

    def save(self):
        self.date = datetime.now()

        super(Change, self).save()

    class Meta:
        unique_together = [("content_type", "object_id")]
