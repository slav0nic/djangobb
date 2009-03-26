import djapian

from apps.forum.models import Post
        
class PostIndexer(djapian.Indexer):
    fields=['body']
    tags=[
        ('user',    'user.username'   ),
        ('topic',   'topic.name'      ),
        ('forum',   'topic.forum.pk'  ),
        ('body',    'body'            ),
        ('created', 'created'         ),
    ]

post_indexer = djapian.add_index(Post, PostIndexer)
