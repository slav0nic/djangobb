import os
import new

from django.db import models
from django.conf import settings
from django.utils.datastructures import SortedDict

from djapian import utils
from djapian.database import Database
from djapian.indexer import Indexer

class IndexSpace(object):
    instances = []

    def __init__(self, base_dir, name):
        self._base_dir = os.path.abspath(base_dir)
        self._indexers = SortedDict()
        self._name = name

        self.__class__.instances.append(self)

    def __unicode__(self):
        return self._name

    def __str__(self):
        from django.utils.encoding import smart_str
        return smart_str(self.__unicode__())

    def add_index(self, model, indexer=None, attach_as=None):
        if indexer is None:
            indexer = self.create_default_indexer(model)

        db = Database(
            os.path.join(
                self._base_dir,
                model._meta.app_label,
                model._meta.object_name.lower(),
                indexer.get_descriptor()
            )
        )

        indexer = indexer(db, model)

        if attach_as is not None:
            if hasattr(model, attach_as):
                raise ValueError("Attribute with name `%s` is already exist" % attach_as)
            else:
                model.add_to_class(attach_as, indexer)

        if model in self._indexers:
            self._indexers[model].append(indexer)
        else:
            self._indexers[model] = [indexer]

        return indexer

    def get_indexers(self):
        return self._indexers

    def get_indexers_for_model(self, model):
        try:
            return self._indexers[model]
        except KeyError:
            return []

    def create_default_indexer(self, model):
        tags = []
        fields = []

        for field in model._meta.field:
            if isinstance(field, models.TestField):
                fields.append(field.attname)
            else:
                tags.append((field.name, field.attname))

        return new.classobj(
            "Default%sIndexer" % utils.model_name(model).replace('.', ''),
            (Indexer,),
            {
                "tags": tags,
                "fields": fields
            }
        )
