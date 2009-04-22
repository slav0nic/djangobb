from django.test import TestCase
from djapian.tests.utils import BaseTestCase, BaseIndexerTest, Entry, Person

class FilteringTest(BaseIndexerTest, BaseTestCase):
    def setUp(self):
        super(FilteringTest, self).setUp()
        self.result = Entry.indexer.search("text")

    def test_filter(self):
        self.assertEqual(self.result.filter(count=5).count(), 1)
        self.assertEqual(self.result.filter(count__lt=6).count(), 2)
        self.assertEqual(self.result.filter(count__gte=5).count(), 2)

        self.assertEqual(self.result.filter(count__in=[5, 7]).count(), 2)

    def test_exclude(self):
        self.assertEqual(self.result.exclude(count=5).count(), 2)
        self.assertEqual(self.result.exclude(count__lt=6).count(), 1)
        self.assertEqual(self.result.exclude(count__gte=5).count(), 1)

    def test_filter_exclude(self):
        self.assertEqual(self.result.filter(count__lt=6).exclude(count=5).count(), 1)
