from haystack.indexes import *
from haystack import site
from celery_haystack.indexes import CelerySearchIndex


import djangobb_forum.models as models

class PostIndex(CelerySearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='user')
    created = DateTimeField(model_attr='created')
    topic = CharField(model_attr='topic')
    category = CharField(model_attr='topic__forum__category__name')
    forum = IntegerField(model_attr='topic__forum__pk')

site.register(models.Post, PostIndex)
