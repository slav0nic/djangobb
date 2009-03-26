from django.test import TestCase

from djapian.tests.utils import BaseIndexerTest, Entry

def query_test(query, count):
    class _QueryTest(BaseIndexerTest, TestCase):
        def setUp(self):
            super(_QueryTest, self).setUp()
            self.result = Entry.indexer.search(query)

        def test_result_count(self):
            self.assertEqual(len(self.result), count)
    _QueryTest.__name__ = _QueryTest.__name__ + '_' + query.replace(" ", "_")
    return _QueryTest

IndexerSearchCharFieldTest = query_test("title:test", 1)
IndexerSearchAliasFieldTest = query_test("subject:test", 1)
IndexerSearchBoolFieldTest = query_test("active:True", 1)
IndexerSearchAndQueryTest = query_test("title:test AND title:another", 0)
