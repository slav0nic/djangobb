# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from djangobb_forum.models import MARKUP_CHOICES, THEME_CHOICES, TZ_CHOICES
import djangobb_forum.fields
import django.utils.timezone
from django.conf import settings
from djangobb_forum import settings as forum_settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('size', models.IntegerField(verbose_name='Size')),
                ('content_type', models.CharField(max_length=255, verbose_name='Content type')),
                ('path', models.CharField(max_length=255, verbose_name='Path')),
                ('name', models.TextField(verbose_name='Name')),
                ('hash', models.CharField(default='', max_length=40, verbose_name='Hash', db_index=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ban',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ban_start', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Ban start')),
                ('ban_end', models.DateTimeField(null=True, verbose_name='Ban end', blank=True)),
                ('reason', models.TextField(verbose_name='Reason')),
                ('user', models.OneToOneField(related_name='ban_users', verbose_name='Banned user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ban',
                'verbose_name_plural': 'Bans',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('position', models.IntegerField(default=0, verbose_name='Position', blank=True)),
                ('groups', models.ManyToManyField(help_text='Only users from these groups can see this category', to='auth.Group', verbose_name='Groups', blank=True)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Forum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=80, verbose_name='Name')),
                ('position', models.IntegerField(default=0, verbose_name='Position', blank=True)),
                ('description', models.TextField(default='', verbose_name='Description', blank=True)),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='Updated')),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('topic_count', models.IntegerField(default=0, verbose_name='Topic count', blank=True)),
                ('forum_logo', djangobb_forum.fields.ExtendedImageField(default='', upload_to=b'djangobb_forum/forum_logo', verbose_name='Forum Logo', blank=True)),
                ('category', models.ForeignKey(related_name='forums', verbose_name='Category', to='djangobb_forum.Category')),
            ],
            options={
                'ordering': ['position'],
                'verbose_name': 'Forum',
                'verbose_name_plural': 'Forums',
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(max_length=200)),
                ('choice_count', models.PositiveSmallIntegerField(default=1, help_text='How many choices are allowed simultaneously.')),
                ('active', models.BooleanField(default=True, help_text='Can users vote to this poll or just see the result?')),
                ('deactivate_date', models.DateTimeField(help_text='Point of time after this poll would be automatic deactivated', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PollChoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice', models.CharField(max_length=200)),
                ('votes', models.IntegerField(default=0, editable=False)),
                ('poll', models.ForeignKey(related_name='choices', to='djangobb_forum.Poll')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', models.DateTimeField(null=True, verbose_name='Updated', blank=True)),
                ('markup', models.CharField(default=forum_settings.DEFAULT_MARKUP, max_length=15, verbose_name='Markup', choices=MARKUP_CHOICES)),
                ('body', models.TextField(verbose_name='Message')),
                ('body_html', models.TextField(verbose_name='HTML version')),
                ('user_ip', models.GenericIPAddressField(null=True, verbose_name='User IP', blank=True)),
            ],
            options={
                'ordering': ['created'],
                'get_latest_by': 'created',
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
        ),
        migrations.CreateModel(
            name='PostTracking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('topics', djangobb_forum.fields.JSONField(null=True, blank=True)),
                ('last_read', models.DateTimeField(null=True, blank=True)),
                ('user', djangobb_forum.fields.AutoOneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Post tracking',
                'verbose_name_plural': 'Post tracking',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.CharField(max_length=30, verbose_name='Status', blank=True)),
                ('site', models.URLField(verbose_name='Site', blank=True)),
                ('jabber', models.CharField(max_length=80, verbose_name='Jabber', blank=True)),
                ('icq', models.CharField(max_length=12, verbose_name='ICQ', blank=True)),
                ('msn', models.CharField(max_length=80, verbose_name='MSN', blank=True)),
                ('aim', models.CharField(max_length=80, verbose_name='AIM', blank=True)),
                ('yahoo', models.CharField(max_length=80, verbose_name='Yahoo', blank=True)),
                ('location', models.CharField(max_length=30, verbose_name='Location', blank=True)),
                ('signature', models.TextField(default='', max_length=1024, verbose_name='Signature', blank=True)),
                ('signature_html', models.TextField(default='', max_length=1024, verbose_name='Signature', blank=True)),
                ('time_zone', models.CharField(default=settings.TIME_ZONE, max_length=50, verbose_name='Time zone', choices=TZ_CHOICES)),
                ('language', models.CharField(default='', max_length=5, verbose_name='Language', choices=settings.LANGUAGES)),
                ('avatar', djangobb_forum.fields.ExtendedImageField(default='', upload_to=b'djangobb_forum/avatars', verbose_name='Avatar', blank=True)),
                ('theme', models.CharField(default='default', max_length=80, verbose_name='Theme', choices=THEME_CHOICES)),
                ('show_avatar', models.BooleanField(default=True, verbose_name='Show avatar')),
                ('show_signatures', models.BooleanField(default=True, verbose_name='Show signatures')),
                ('show_smilies', models.BooleanField(default=True, verbose_name='Show smilies')),
                ('privacy_permission', models.IntegerField(default=1, verbose_name='Privacy permission', choices=[(0, 'Display your e-mail address.'), (1, 'Hide your e-mail address but allow form e-mail.'), (2, 'Hide your e-mail address and disallow form e-mail.')])),
                ('auto_subscribe', models.BooleanField(default=False, help_text='Auto subscribe all topics you have created or reply.', verbose_name='Auto subscribe')),
                ('markup', models.CharField(default=forum_settings.DEFAULT_MARKUP, max_length=15, verbose_name='Default markup', choices=MARKUP_CHOICES)),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('user', djangobb_forum.fields.AutoOneToOneField(related_name='forum_profile', verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zapped', models.BooleanField(default=False, verbose_name='Zapped')),
                ('created', models.DateTimeField(verbose_name='Created', blank=True)),
                ('reason', models.TextField(default='', max_length='1000', verbose_name='Reason', blank=True)),
                ('post', models.ForeignKey(verbose_name='Post', to='djangobb_forum.Post')),
                ('reported_by', models.ForeignKey(related_name='reported_by', verbose_name='Reported by', to=settings.AUTH_USER_MODEL)),
                ('zapped_by', models.ForeignKey(related_name='zapped_by', verbose_name='Zapped by', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
        migrations.CreateModel(
            name='Reputation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Time')),
                ('sign', models.IntegerField(default=0, verbose_name='Sign', choices=[(1, 'PLUS'), (-1, 'MINUS')])),
                ('reason', models.TextField(max_length=1000, verbose_name='Reason')),
                ('from_user', models.ForeignKey(related_name='reputations_from', verbose_name='From', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(related_name='post', verbose_name='Post', to='djangobb_forum.Post')),
                ('to_user', models.ForeignKey(related_name='reputations_to', verbose_name='To', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reputation',
                'verbose_name_plural': 'Reputations',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Subject')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
                ('updated', models.DateTimeField(null=True, verbose_name='Updated')),
                ('views', models.IntegerField(default=0, verbose_name='Views count', blank=True)),
                ('sticky', models.BooleanField(default=False, verbose_name='Sticky')),
                ('closed', models.BooleanField(default=False, verbose_name='Closed')),
                ('post_count', models.IntegerField(default=0, verbose_name='Post count', blank=True)),
                ('forum', models.ForeignKey(related_name='topics', verbose_name='Forum', to='djangobb_forum.Forum')),
                ('last_post', models.ForeignKey(related_name='last_topic_post', blank=True, to='djangobb_forum.Post', null=True)),
                ('subscribers', models.ManyToManyField(related_name='subscriptions', verbose_name='Subscribers', to=settings.AUTH_USER_MODEL, blank=True)),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated'],
                'get_latest_by': 'updated',
                'verbose_name': 'Topic',
                'verbose_name_plural': 'Topics',
            },
        ),
        migrations.AddField(
            model_name='post',
            name='topic',
            field=models.ForeignKey(related_name='posts', verbose_name='Topic', to='djangobb_forum.Topic'),
        ),
        migrations.AddField(
            model_name='post',
            name='updated_by',
            field=models.ForeignKey(verbose_name='Updated by', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(related_name='posts', verbose_name='User', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='poll',
            name='topic',
            field=models.ForeignKey(to='djangobb_forum.Topic'),
        ),
        migrations.AddField(
            model_name='poll',
            name='users',
            field=models.ManyToManyField(help_text='Users who has voted this poll.', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='forum',
            name='last_post',
            field=models.ForeignKey(related_name='last_forum_post', blank=True, to='djangobb_forum.Post', null=True),
        ),
        migrations.AddField(
            model_name='forum',
            name='moderators',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Moderators', blank=True),
        ),
        migrations.AddField(
            model_name='attachment',
            name='post',
            field=models.ForeignKey(related_name='attachments', verbose_name='Post', to='djangobb_forum.Post'),
        ),
        migrations.AlterUniqueTogether(
            name='reputation',
            unique_together=set([('from_user', 'post')]),
        ),
    ]
