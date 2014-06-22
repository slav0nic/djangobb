from django.utils.timezone import now 
from haystack import indexes

from djangobb_forum.models import Post
 
 
class PostIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	author = indexes.CharField(model_attr='user')
	created = indexes.DateTimeField(model_attr='created')
	topic = indexes.CharField(model_attr='topic')
	category = indexes.CharField(model_attr='topic__forum__category__name')
	forum = indexes.IntegerField(model_attr='topic__forum__pk')
 
	def get_model(self):
		return Post
 
	def index_queryset(self, using=None):
		# TODO: reindex updated Posts
		return self.get_model().objects.filter(created__lte=now())
