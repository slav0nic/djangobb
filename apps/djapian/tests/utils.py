# -*- coding: utf-8 -*-
import os
from datetime import datetime

from django.db import models
from django.test import TestCase

import djapian
from djapian import Indexer, Field

class Person(models.Model):
    name = models.CharField(max_length=150)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "djapian"

class Entry(models.Model):
    author = models.ForeignKey(Person, related_name="entries")
    title = models.CharField(max_length=250)
    tags = models.CharField(max_length=250, null=True)
    created_on = models.DateTimeField(default=datetime.now)

    asset_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    text = models.TextField()

    editors = models.ManyToManyField(Person, related_name="edited_entries")

    def headline(self):
        return "%s - %s" % (self.author, self.title)

    def __unicode__(self):
        return self.title

    class Meta:
        app_label = "djapian"

class EntryIndexer(Indexer):
    fields=["text"]
    tags=[
        ("author", "author.name"),
        ("title", "title", 3),
        ("tag", "tags", 2),
        ("date", "created_on"),
        ("active", "is_active"),
        ("count", "asset_count"),
        ("editors", "editors"),
    ]
    aliases={
        "title": "subject",
        "author": "user",
    }
    trigger=lambda indexer, obj: obj.is_active

indexer = djapian.add_index(Entry, EntryIndexer, attach_as="indexer")

class BaseTestCase(TestCase):
    def tearDown(self):
        Entry.indexer.clear()

class BaseIndexerTest(object):
    def setUp(self):
        p = Person.objects.create(name="Alex")

        self.entries= [
            Entry.objects.create(
                author=p,
                title="Test entry",
                text="Not large text field"
            ),
            Entry.objects.create(
                author=p,
                title="Another test entry",
                is_active=False
            )
        ]

        Entry.indexer.update()
