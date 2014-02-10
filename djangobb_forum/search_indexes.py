from haystack.indexes import *
from haystack import site

from gargoyle import gargoyle
try:
    if gargoyle.is_active('solr_indexing_enabled'):
        from celery_haystack.indexes import CelerySearchIndex as SearchIndex
except:
    # Allow migrations to run
    from celery_haystack.indexes import CelerySearchIndex as SearchIndex


import djangobb_forum.models as models

class PostIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='user')
    created = DateTimeField(model_attr='created')
    topic = CharField(model_attr='topic')
    category = CharField(model_attr='topic__forum__category__name')
    forum = IntegerField(model_attr='topic__forum__pk')

site.register(models.Post, PostIndex)
