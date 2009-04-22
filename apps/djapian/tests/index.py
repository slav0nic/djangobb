import os
from datetime import datetime

from django.db import models

from djapian import Indexer, Field
from djapian.tests.utils import BaseTestCase, BaseIndexerTest, Entry, Person

class IndexerUpdateTest(BaseIndexerTest, BaseTestCase):
    def test_database_exists(self):
        self.assert_(os.path.exists(Entry.indexer._db._path))

    def test_document_count(self):
        self.assertEqual(Entry.indexer.document_count(), 3)

class IndexCommandTest(BaseTestCase):
    def setUp(self):
        p = Person.objects.create(name="Alex")
        entry1 = Entry.objects.create(
            author=p,
            title="Test entry",
            text="Not large text field"
        )
        entry2 = Entry.objects.create(
            author=p,
            title="Another test entry",
            is_active=False
        )

        from django.core.management import call_command

        call_command("index", no_fork=True, once=True)

    def test_database(self):
        self.assertEqual(Entry.indexer.document_count(), 1)
