import os

from django.conf import settings

from djapian.indexer import Field, Indexer
from djapian.database import Database
from djapian.utils import load_indexes

indexer_map = {}

def add_index(model, indexer=None, attach_as=None, db=None):
    if db is None:
        db = Database(
            os.path.join(
                settings.DJAPIAN_DATABASE_PATH,
                model._meta.app_label,
                model._meta.object_name.lower(),
                indexer.get_descriptor()
            )
        )

    indexer = db.add_index(model, indexer, attach_as)

    if model in indexer_map:
        indexer_map[model].append(indexer)
    else:
        indexer_map[model] = [indexer]

    return indexer
