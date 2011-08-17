# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('djangobb_forum_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('djangobb_forum', ['Category'])

        # Adding M2M table for field groups on 'Category'
        db.create_table('djangobb_forum_category_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('category', models.ForeignKey(orm['djangobb_forum.category'], null=False)),
            ('group', models.ForeignKey(orm['auth.group'], null=False))
        ))
        db.create_unique('djangobb_forum_category_groups', ['category_id', 'group_id'])

        # Adding model 'Forum'
        db.create_table('djangobb_forum_forum', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(related_name='forums', to=orm['djangobb_forum.Category'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('post_count', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('topic_count', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('last_post', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_forum_post', null=True, to=orm['djangobb_forum.Post'])),
        ))
        db.send_create_signal('djangobb_forum', ['Forum'])

        # Adding M2M table for field moderators on 'Forum'
        db.create_table('djangobb_forum_forum_moderators', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('forum', models.ForeignKey(orm['djangobb_forum.forum'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('djangobb_forum_forum_moderators', ['forum_id', 'user_id'])

        # Adding model 'Topic'
        db.create_table('djangobb_forum_topic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('forum', self.gf('django.db.models.fields.related.ForeignKey')(related_name='topics', to=orm['djangobb_forum.Forum'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('views', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('sticky', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('post_count', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('last_post', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='last_topic_post', null=True, to=orm['djangobb_forum.Post'])),
        ))
        db.send_create_signal('djangobb_forum', ['Topic'])

        # Adding M2M table for field subscribers on 'Topic'
        db.create_table('djangobb_forum_topic_subscribers', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(orm['djangobb_forum.topic'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('djangobb_forum_topic_subscribers', ['topic_id', 'user_id'])

        # Adding model 'Post'
        db.create_table('djangobb_forum_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posts', to=orm['djangobb_forum.Topic'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posts', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('markup', self.gf('django.db.models.fields.CharField')(default='bbcode', max_length=15)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('body_html', self.gf('django.db.models.fields.TextField')()),
            ('user_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal('djangobb_forum', ['Post'])

        # Adding model 'Reputation'
        db.create_table('djangobb_forum_reputation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reputations_from', to=orm['auth.User'])),
            ('to_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reputations_to', to=orm['auth.User'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='post', to=orm['djangobb_forum.Post'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sign', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('reason', self.gf('django.db.models.fields.TextField')(max_length=1000)),
        ))
        db.send_create_signal('djangobb_forum', ['Reputation'])

        # Adding unique constraint on 'Reputation', fields ['from_user', 'post']
        db.create_unique('djangobb_forum_reputation', ['from_user_id', 'post_id'])

        # Adding model 'Profile'
        db.create_table('djangobb_forum_profile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('djangobb_forum.fields.AutoOneToOneField')(related_name='forum_profile', unique=True, to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('site', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('jabber', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('icq', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('msn', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('aim', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('yahoo', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('signature', self.gf('django.db.models.fields.TextField')(default='', max_length=1024, blank=True)),
            ('time_zone', self.gf('django.db.models.fields.FloatField')(default=3.0)),
            ('language', self.gf('django.db.models.fields.CharField')(default='', max_length=5)),
            ('avatar', self.gf('djangobb_forum.fields.ExtendedImageField')(default='', max_length=100, blank=True)),
            ('theme', self.gf('django.db.models.fields.CharField')(default='default', max_length=80)),
            ('show_avatar', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('show_signatures', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('privacy_permission', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('markup', self.gf('django.db.models.fields.CharField')(default='bbcode', max_length=15)),
            ('post_count', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('djangobb_forum', ['Profile'])

        # Adding model 'PostTracking'
        db.create_table('djangobb_forum_posttracking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('djangobb_forum.fields.AutoOneToOneField')(to=orm['auth.User'], unique=True)),
            ('topics', self.gf('djangobb_forum.fields.JSONField')(null=True)),
            ('last_read', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('djangobb_forum', ['PostTracking'])

        # Adding model 'Report'
        db.create_table('djangobb_forum_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reported_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='reported_by', to=orm['auth.User'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangobb_forum.Post'])),
            ('zapped', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('zapped_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='zapped_by', null=True, to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('reason', self.gf('django.db.models.fields.TextField')(default='', max_length='1000', blank=True)),
        ))
        db.send_create_signal('djangobb_forum', ['Report'])

        # Adding model 'Ban'
        db.create_table('djangobb_forum_ban', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(related_name='ban_users', unique=True, to=orm['auth.User'])),
            ('ban_start', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('ban_end', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('reason', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djangobb_forum', ['Ban'])

        # Adding model 'Attachment'
        db.create_table('djangobb_forum_attachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['djangobb_forum.Post'])),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('content_type', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name', self.gf('django.db.models.fields.TextField')()),
            ('hash', self.gf('django.db.models.fields.CharField')(default='', max_length=40, db_index=True, blank=True)),
        ))
        db.send_create_signal('djangobb_forum', ['Attachment'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Reputation', fields ['from_user', 'post']
        db.delete_unique('djangobb_forum_reputation', ['from_user_id', 'post_id'])

        # Deleting model 'Category'
        db.delete_table('djangobb_forum_category')

        # Removing M2M table for field groups on 'Category'
        db.delete_table('djangobb_forum_category_groups')

        # Deleting model 'Forum'
        db.delete_table('djangobb_forum_forum')

        # Removing M2M table for field moderators on 'Forum'
        db.delete_table('djangobb_forum_forum_moderators')

        # Deleting model 'Topic'
        db.delete_table('djangobb_forum_topic')

        # Removing M2M table for field subscribers on 'Topic'
        db.delete_table('djangobb_forum_topic_subscribers')

        # Deleting model 'Post'
        db.delete_table('djangobb_forum_post')

        # Deleting model 'Reputation'
        db.delete_table('djangobb_forum_reputation')

        # Deleting model 'Profile'
        db.delete_table('djangobb_forum_profile')

        # Deleting model 'PostTracking'
        db.delete_table('djangobb_forum_posttracking')

        # Deleting model 'Report'
        db.delete_table('djangobb_forum_report')

        # Deleting model 'Ban'
        db.delete_table('djangobb_forum_ban')

        # Deleting model 'Attachment'
        db.delete_table('djangobb_forum_attachment')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangobb_forum.attachment': {
            'Meta': {'object_name': 'Attachment'},
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'hash': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '40', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['djangobb_forum.Post']"}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'djangobb_forum.ban': {
            'Meta': {'object_name': 'Ban'},
            'ban_end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ban_start': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'ban_users'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'djangobb_forum.category': {
            'Meta': {'ordering': "['position']", 'object_name': 'Category'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.Group']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'djangobb_forum.forum': {
            'Meta': {'ordering': "['position']", 'object_name': 'Forum'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forums'", 'to': "orm['djangobb_forum.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_post': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_forum_post'", 'null': 'True', 'to': "orm['djangobb_forum.Post']"}),
            'moderators': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'post_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'topic_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'djangobb_forum.post': {
            'Meta': {'ordering': "['created']", 'object_name': 'Post'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'body_html': ('django.db.models.fields.TextField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'bbcode'", 'max_length': '15'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': "orm['djangobb_forum.Topic']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posts'", 'to': "orm['auth.User']"}),
            'user_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'})
        },
        'djangobb_forum.posttracking': {
            'Meta': {'object_name': 'PostTracking'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_read': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'topics': ('djangobb_forum.fields.JSONField', [], {'null': 'True'}),
            'user': ('djangobb_forum.fields.AutoOneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'djangobb_forum.profile': {
            'Meta': {'object_name': 'Profile'},
            'aim': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'avatar': ('djangobb_forum.fields.ExtendedImageField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'icq': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jabber': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'markup': ('django.db.models.fields.CharField', [], {'default': "'bbcode'", 'max_length': '15'}),
            'msn': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'post_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'privacy_permission': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'show_avatar': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_signatures': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'signature': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '1024', 'blank': 'True'}),
            'site': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'theme': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '80'}),
            'time_zone': ('django.db.models.fields.FloatField', [], {'default': '3.0'}),
            'user': ('djangobb_forum.fields.AutoOneToOneField', [], {'related_name': "'forum_profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'yahoo': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        },
        'djangobb_forum.report': {
            'Meta': {'object_name': 'Report'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangobb_forum.Post']"}),
            'reason': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': "'1000'", 'blank': 'True'}),
            'reported_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reported_by'", 'to': "orm['auth.User']"}),
            'zapped': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zapped_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'zapped_by'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'djangobb_forum.reputation': {
            'Meta': {'unique_together': "(('from_user', 'post'),)", 'object_name': 'Reputation'},
            'from_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reputations_from'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'post'", 'to': "orm['djangobb_forum.Post']"}),
            'reason': ('django.db.models.fields.TextField', [], {'max_length': '1000'}),
            'sign': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'to_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reputations_to'", 'to': "orm['auth.User']"})
        },
        'djangobb_forum.topic': {
            'Meta': {'ordering': "['-updated']", 'object_name': 'Topic'},
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'forum': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'topics'", 'to': "orm['djangobb_forum.Forum']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_post': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'last_topic_post'", 'null': 'True', 'to': "orm['djangobb_forum.Post']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'post_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'sticky': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subscribers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'subscriptions'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        }
    }

    complete_apps = ['djangobb_forum']
