import sys
import cmd
from django.core.management.base import BaseCommand

from djapian import utils
import djapian

def with_index(func):
    def _decorator(cmd, arg):
        if cmd._current_index is None:
            print "No index selected"
            return

        return func(cmd, arg)
    _decorator.__doc__ = func.__doc__
    return _decorator

class Interpreter(cmd.Cmd):
    prompt = ">>> "

    def __init__(self, *args):
        self._list = djapian.indexer_map.items()
        self._current_index = None

        if len(args):
            self.do_use(args[0])

        cmd.Cmd.__init__(self)

    def do_list(self, arg):
        """
        Lists all available indexes with their ids
        """
        for i, pair in enumerate(self._list):
            model, indexers = pair
            print "%s: `%s` by:" % (i, utils.model_name(model))
            for j, indexer in enumerate(indexers):
                print "\t%s.%s: %s" % (i, j, indexer)

    def do_exit(self, arg):
        """
        Exit shell
        """
        return True

    def do_use(self, index):
        """
        Changes current index
        """
        model, indexer = map(int, index.split('.'))
        self._current_index = self._list[model][1][indexer]
        print "Using `%s by %s` index." % (utils.model_name(self._list[model][0]), self._list[model][1][indexer])

    @with_index
    def do_query(self, query):
        """
        Returns objects fetched by given query
        """
        print list(self._current_index.search(query))

    @with_index
    def do_count(self, query):
        """
        Returns count of objects fetched by given query
        """
        print self._current_index.search(query).count()

    @with_index
    def do_total(self, arg):
        """
        Returns count of objects in index
        """
        print self._current_index.document_count()

    def do_stats(self, arg):
        """
        Print index status information
        """
        import operator
        print "Number of indexes: %s" % reduce(operator.add, [len(indexes) for model, indexes in self._list])

    @with_index
    def do_docslist(self, slice=""):
        """
        Returns count of objects in index
        """
        db = self._current_index._db.open()

        start, end = self._parse_slice(slice, db.get_lastdocid())

        for i in range(start, end + 1):
            doc = db.get_document(i)
            print "doc #%s:\n\tValues (%s):" % (i, doc.values_count())
            val = doc.values_begin()

            for i in range(doc.values_count()):
                print "\t\t%s: %s" % (val.get_valueno(), val.get_value())
                val.next()

            print "\tTerms (%s):" % doc.termlist_count()
            termlist = doc.termlist_begin()

            for i in range(doc.termlist_count()):
                print termlist.get_term(),
                termlist.next()
            print "\n"

    @with_index
    def do_delete(self, id):
        """
        Removes document by id
        """
        id = int(id)

        db = self._current_index._db.open(write=True)
        db.delete_document(id)
        print "Document #%s deleted." % id

    def _parse_slice(self, slice="", last=None):
        if slice:
            bits = slice.split(':')
            if len(bits) == 2:
                start, end = map(int, bits)
            else:
                start = end = int(bits[0])
        else:
            start = 1
            end = last

        end = min(end, last)

        return start, end

class Command(BaseCommand):
    help = "Djapian shell that provides capabilities to monitoring indexes."
    args = '[index_id]'

    requires_model_validation = True

    def handle(self, *args, **options):
        utils.load_indexes()

        try:
            Interpreter(*args).cmdloop("Interactive Djapian shell.")
        except KeyboardInterrupt:
            print "\n"
