# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('djangobb_forum', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='groups',
            field=models.ManyToManyField(blank=True, verbose_name='Groups', help_text='Only users from these groups can see this category', to='auth.Group'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='forum',
            name='moderators',
            field=models.ManyToManyField(blank=True, verbose_name='Moderators', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='poll',
            name='users',
            field=models.ManyToManyField(blank=True, help_text='Users who has voted this poll.', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
