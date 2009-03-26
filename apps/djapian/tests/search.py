from django.test import TestCase
from djapian.tests.utils import BaseTestCase, BaseIndexerTest, Entry, Person

class IndexerSearchTextTest(BaseIndexerTest, BaseTestCase):
    def setUp(self):
        super(IndexerSearchTextTest, self).setUp()
        self.result = Entry.indexer.search("text")

    def test_result_count(self):
        self.assertEqual(len(self.result), 1)

    def test_result_row(self):
        self.assertEqual(self.result[0].instance, self.entries[0])

    def test_result_list(self):
        self.assertEqual([r.instance for r in self.result], self.entries[0:1])

    def test_score(self):
        self.assert_(self.result[0].percent in (99, 100))

class AliasesTest(BaseTestCase):
    num_entries = 10

    def setUp(self):
        p = Person.objects.create(name="Alex")

        for i in range(self.num_entries):
            Entry.objects.create(author=p, title="Entry with number %s" % i, text="foobar " * i)

        Entry.indexer.update()

        self.result = Entry.indexer.search("subject:number")

    def test_result(self):
        self.assertEqual(len(self.result), 10)

class CorrectedQueryStringTest(BaseIndexerTest, BaseTestCase):
    def test_correction(self):
        results = Entry.indexer.search("texte").spell_correction()

        self.assertEqual(results.get_corrected_query_string(), "text")
