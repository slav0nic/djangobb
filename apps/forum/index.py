import djapian

from forum.models import Post
        
class PostIndexer(djapian.Indexer):
    fields=['body']
    tags=[
        ('user',    'user.username'   ),
        ('topic',   'topic.name'      ),
        ('forum',   'topic.forum.pk'  ),
        ('body',    'body'            ),
        ('created', 'created'         ),
    ]

    trigger = ( lambda post: not post.topic.forum.category.groups.count() )


post_indexer = djapian.add_index(Post, PostIndexer)
