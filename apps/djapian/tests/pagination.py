from django.core.paginator import Paginator

from djapian.tests.utils import BaseTestCase, Entry, Person

class ResultSetPaginationTest(BaseTestCase):
    num_entries = 100
    per_page = 10
    num_pages = num_entries / per_page

    def setUp(self):
        p = Person.objects.create(name="Alex")

        for i in range(self.num_entries):
            Entry.objects.create(
                author=p,
                title="Entry with number %s" % i,
                text="foobar " * i
            )

        Entry.indexer.update()

        self.result = Entry.indexer.search("title:number")

    def test_pagintion(self):
        paginator = Paginator(self.result, self.per_page)

        self.assertEqual(paginator.num_pages, self.num_pages)

        page = paginator.page(5)
