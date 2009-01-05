from django.db import connection

from apps.forum.models import Forum, Topic

DESCRIPTION = 'Add and populate post_count fields to Forum and Topic models'

def migrate():
    cur = connection.cursor()

    print 'Altering forum table'
    cur.execute("ALTER TABLE forum_forum ADD post_count INT NOT NULL DEFAULT 0")

    print 'Altering topic table'
    cur.execute("ALTER TABLE forum_topic ADD post_count INT NOT NULL DEFAULT 0")

    print 'Populating post_count of topics'
    for topic in Topic.objects.all():
        topic.post_count = topic.posts.all().count()
        topic.save()

    print 'Populating post_count of forums'
    for forum in Forum.objects.all():
        forum.post_count = sum(x.post_count for x in forum.topics.all())
        forum.save()
