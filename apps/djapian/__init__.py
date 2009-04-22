from django.conf import settings

from djapian.indexer import Field, Indexer
from djapian.database import Database
from djapian.space import IndexSpace
from djapian.utils import load_indexes

space = IndexSpace(settings.DJAPIAN_DATABASE_PATH, "global")

add_index = space.add_index
