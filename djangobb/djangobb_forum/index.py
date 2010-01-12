import djapian

from djangobb_forum.models import Post


class PostIndexer(djapian.Indexer):
    fields=['body']
    tags=[
        ('user',    'user.username'   ),
        ('topic',   'topic.name'      ),
        ('forum',   'topic.forum.pk'  ),
        ('body',    'body'            ),
        ('created', 'created'         ),
    ]

    trigger = lambda indexer, post: not post.topic.forum.category.groups.count()


post_indexer = djapian.add_index(Post, PostIndexer)
