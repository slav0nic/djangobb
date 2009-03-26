import os

from djapian import Field
from djapian.tests.utils import BaseTestCase, BaseIndexerTest, Entry, Person
from djapian.models import Change
from django.utils.encoding import force_unicode

class IndexerTest(BaseTestCase):
    def test_text_fields_count(self):
        self.assertEqual(len(Entry.indexer.fields), 1)

    def test_attributes_count(self):
        self.assertEqual(len(Entry.indexer.tags), 7)

class FieldResolverTest(BaseTestCase):
    def setUp(self):
        p = Person.objects.create(name="Alex")
        self.entry = Entry.objects.create(author=p, title="Test entry")

    def test_simple_attribute(self):
        self.assertEqual(Field("title").resolve(self.entry), "Test entry")

    def test_related_attribute(self):
        self.assertEqual(Field("author.name").resolve(self.entry), "Alex")

    def test_fk_attribute(self):
        self.assertEqual(force_unicode(Field("author").resolve(self.entry)), "Alex")

    def test_method(self):
        self.assertEqual(
            Field("headline").resolve(self.entry),
            "Alex - Test entry"
        )

class ChangeTrackingTest(BaseTestCase):
    def setUp(self):
        p = Person.objects.create(name="Alex")
        Entry.objects.create(author=p, title="Test entry")
        Entry.objects.create(
            author=p,
            title="Another test entry",
            is_active=False
        )

    def test_change_count(self):
        self.assertEqual(Change.objects.count(), 2)

class ChangeTrackingUpdateTest(BaseTestCase):
    def setUp(self):
        p = Person.objects.create(name="Alex")
        entry = Entry.objects.create(author=p, title="Test entry")

        entry.title = "Foobar title"
        entry.save()

    def test_change_count(self):
        self.assertEqual(Change.objects.count(), 1)

    def test_change_action(self):
        self.assertEqual(Change.objects.get().action, "add")

class ChangeTrackingDeleteTest(BaseTestCase):
    def setUp(self):
        p = Person.objects.create(name="Alex")
        entry = Entry.objects.create(author=p, title="Test entry")
        entry.delete()

    def test_change_count(self):
        self.assertEqual(Change.objects.count(), 0)
