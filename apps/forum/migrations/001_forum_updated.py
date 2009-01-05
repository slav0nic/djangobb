from django.db import connection

from apps.forum.models import Forum, Topic

DESCRIPTION = 'Add updated column to forum table'

def migrate():
    cur = connection.cursor()

    print 'Altering forum table'
    cur.execute("ALTER TABLE forum_forum ADD updated DATETIME NULL")

    print 'Fixing updated values of forums'
    for forum in Forum.objects.all():
        try:
            topic = forum.topics.all().order_by('-updated')[0]
        except IndexError:
            pass
        else:
            forum.updated = topic.updated
            forum.save()


