import sqlalchemy as SA
from sqlalchemy import sql
from datetime import datetime
import os
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from forum.models import Category, Forum, Topic, Post, Profile
from forums.lib import phpserialize

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--user', help=u'Punbb DB username'),
        make_option('--password', help=u'Punbb DB password'),
        make_option('--host', default='localhost', help=u'Punbb DB host'),
        make_option('--port', help=u'Punbb DB port'),
        make_option('--encoding', default='cp1251', help=u'Punbb DB encoding'),
        make_option('--mysql-encoding', help=u'Punbb DB encoding. I can\'t explain this yet'),
        make_option('--engine', default='mysql', help=u'Punbb DB engine [postgres, mysql etc]'),
        make_option('--prefix', default='punbb_', help=u'Punbb DB tables prefix'),
    )
    help = u'Imports Punbb database. Attention: old contents of forum database will be removed'
    args = '<db name>'

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError('Punbb database name required')
        else:
            DBNAME = args[0]
        ENCODING = options['encoding']
        MYSQL_ENCODING = options['mysql_encoding']
        PREFIX = options['prefix']

        uri = '%s://' % options['engine']
        if options['user'] is not None:
            uri += options['user']
        if options['password'] is not None:
            uri += ':%s' % options['password']
        if options['host'] is not None:
            uri += '@%s' % options['host']
        if options['port'] is not None:
            uri += ':%s' % options['port']
        uri += '/%s' % DBNAME

        if options['engine'] == 'mysql' and not MYSQL_ENCODING:
            uri += '?charset=%s' % ENCODING.replace('-', '')

        engine = SA.create_engine(uri, convert_unicode=False)
        conn = engine.connect()

        meta = SA.MetaData()
        meta.bind = engine

        users_table = SA.Table(PREFIX + 'users', meta, autoload=True)
        cats_table = SA.Table(PREFIX + 'categories', meta, autoload=True)
        forums_table = SA.Table(PREFIX + 'forums', meta, autoload=True)
        topics_table = SA.Table(PREFIX + 'topics', meta, autoload=True)
        posts_table = SA.Table(PREFIX + 'posts', meta, autoload=True)
        groups_table = SA.Table(PREFIX + 'groups', meta, autoload=True)
        config_table = SA.Table(PREFIX + 'config', meta, autoload=True)
        subscriptions_table = SA.Table(PREFIX + 'subscriptions', meta, autoload=True)

        def decode(data):
            if data is None:
                return None
            if options['engine'] != 'mysql' or MYSQL_ENCODING:
                return data.decode(ENCODING, 'replace')
            else:
                return data

        # Import begins
        print 'Searching admin group'

        ADMIN_GROUP = None
        for count, row in enumerate(conn.execute(sql.select([groups_table]))):
            if row['g_title'] == 'Administrators':
                print 'Admin group was found'
                ADMIN_GROUP = row['g_id']

        if ADMIN_GROUP is None:
            print 'Admin group was NOT FOUND'


        print 'Importing users'
        users = {}
        User.objects.all().delete()

        count = 0
        for count, row in enumerate(conn.execute(sql.select([users_table]))):
            joined = datetime.fromtimestamp(row['registered'])
            last_login = datetime.fromtimestamp(row['last_visit'])
            if len(row['password']) == 40:
                hash = 'sha1$$' + row['password']
            else:
                hash = 'md5$$' + row['password']
            user = User(username=decode(row['username']),
                        email=row['email'],
                        first_name=decode((row['realname'] or '')[:30]),
                        date_joined=joined,
                        last_login=last_login,
                        password=hash
                        )
            if row['group_id'] == ADMIN_GROUP:
                print u'Admin was found: %s' % row['username']
                user.is_superuser = True
                user.is_staff = True

            try:
                user.save()
            except Exception, ex:
                print ex
            else:
                users[row['id']] = user

                profile = user.forum_profile
                profile.jabber = decode(row['jabber'])
                profile.icq = decode(row['icq'])
                profile.yahoo = decode(row['yahoo'])
                profile.msn = decode(row['msn'])
                profile.aim = decode(row['aim'])
                profile.location = decode(row['location'])
                profile.signature = decode(row['signature'])
                profile.show_signatures = bool(row['show_sig'])
                profile.time_zone = row['timezone']

        print 'Total: %d' % (count + 1)
        print 'Imported: %d' % len(users)
        print

        print 'Importing categories'
        cats = {}
        Category.objects.all().delete()

        count = 0
        for count, row in enumerate(conn.execute(sql.select([cats_table]))):
            cat = Category(name=decode(row['cat_name']),
                           position=row['disp_position'])
            cat.save()
            cats[row['id']] = cat

        print 'Total: %d' % (count + 1)
        print 'Imported: %d' % len(cats)
        print

        print 'Importing forums'
        forums = {}
        moderators = {}
        Forum.objects.all().delete()

        count = 0
        for count, row in enumerate(conn.execute(sql.select([forums_table]))):
            if row['last_post']:
                updated = datetime.fromtimestamp(row['last_post'])
            else:
                updated = None

            forum = Forum(name=decode(row['forum_name']),
                          position=row['disp_position'],
                          description=decode(row['forum_desc'] or ''),
                          category=cats[row['cat_id']])
            forum.save()
            forums[row['id']] = forum

            forum._forum_updated = updated

            if row['moderators']:
                for username in phpserialize.loads(row['moderators']).iterkeys():
                    user = User.objects.get(username=username)
                    forum.moderators.add(user)
                    moderators[user.id] = user

        print 'Total: %d' % (count + 1)
        print 'Imported: %d' % len(forums)
        print 'Total number of moderators: %d' % len(moderators)
        print


        print 'Importing topics'
        topics = {}
        moved_count = 0
        Topic.objects.all().delete()

        count = 0
        for count, row in enumerate(conn.execute(sql.select([topics_table]))):
            created = datetime.fromtimestamp(row['posted'])
            updated = datetime.fromtimestamp(row['last_post'])

            # Skip moved topics
            if row['moved_to']:
                moved_count += 1
                continue

            username = decode(row['poster'])
            #testuser = users.values()[0]
            for id, testuser in users.iteritems():
                if testuser.username == username:
                    user = testuser
                    break

            topic = Topic(name=decode(row['subject']),
                          forum=forums[row['forum_id']],
                          views=row['num_views'],
                          sticky=bool(row['sticky']),
                          closed=bool(row['closed']),
                          user=user)
            topic.save()
            topic._forum_updated = updated
            topic._forum_created = created
            topic._forum_punbb_id = row['id']
            topic._forum_posts = 0
            #print topic._forum_updated
            topics[row['id']] = topic

        print 'Total: %d' % (count + 1)
        print 'Imported: %d' % len(topics)
        print 'Moved: %d' % moved_count
        print


        print 'Importing posts'
        posts = {}
        Post.objects.all().delete()

        imported = 0
        count = 0
        for count, row in enumerate(conn.execute(sql.select([posts_table]))):
            created = datetime.fromtimestamp(row['posted'])
            updated = row['edited'] and datetime.fromtimestamp(row['edited']) or None

            if not row['poster_id'] in users:
                print 'post #%d, poster_id #%d does not exist' % (row['id'], row['poster_id'])
                continue

            post = Post(topic=topics[row['topic_id']],
                        created=created,
                        updated=updated,
                        markup='bbcode',
                        user=users[row['poster_id']],
                        user_ip=row['poster_ip'],
                        body=decode(row['message']))
            
            post.save()
            imported += 1
            topics[row['topic_id']]._forum_posts += 1

            # Not actual hack
            ## postmarkups feels bad on some posts :-/
            #try:
                #post.save()
            #except Exception, ex:
                #print post.id, ex
                #print decode(row['message'])
                #print
            #else:
                #imported += 1
                #topics[row['topic_id']]._forum_posts += 1
                ##posts[row['id']] = topic

        print 'Total: %d' % (count + 1)
        print 'Imported: %d' % imported
        print


        print 'Importing subscriptions'

        count = 0
        for count, row in enumerate(conn.execute(sql.select([subscriptions_table]))):
            user = users[row['user_id']]
            topic = topics[row['topic_id']]
            topic.subscribers.add(user)

        print 'Imported: %d' % count


        print 'Restoring topics updated and created values'
        for topic in topics.itervalues():
            topic.updated = topic._forum_updated
            topic.created = topic._forum_created
            topic.save()
        print


        print 'Restoring forums updated and created values'
        for forum in forums.itervalues():
            forum.updated = forum._forum_updated
            forum.save()
        print


        print 'Importing config'
        for row in conn.execute(sql.select([config_table])):
            if row['conf_name'] == 'o_announcement_message':
                value = decode(row['conf_value'])
                if value:
                    open('forum_announcement.txt', 'w').write(value.encode('utf-8'))
                    print 'Not empty announcement found and saved to forum_announcement.txt'
                    print 'If you need announcement write FORUM_NOTICE = " ... text ... " to settings file'
