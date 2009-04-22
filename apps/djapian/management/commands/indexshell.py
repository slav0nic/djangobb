import sys
import cmd

from django.core.management.base import BaseCommand
from django.utils.text import smart_split

from djapian import utils
from djapian import IndexSpace

def with_index(func):
    def _decorator(cmd, arg):
        if cmd._current_index is None:
            print "No index selected"
            return

        return func(cmd, arg)
    _decorator.__doc__ = func.__doc__
    return _decorator

def split_arg(func):
    def _decorator(cmd, arg):
        bits = list(smart_split(arg))

        return func(cmd, bits)
    _decorator.__doc__ = func.__doc__
    return _decorator

class Interpreter(cmd.Cmd):
    prompt = ">>> "

    def __init__(self, *args):
        self._current_index = None

        if len(args):
            self.do_use(args[0])

        cmd.Cmd.__init__(self)

    def do_list(self, arg):
        """
        Lists all available indexes with their ids
        """
        print "Installed spaces/models/indexers:"
        for space_i, space in enumerate(IndexSpace.instances):
            print "%s: `%s`" % (space_i, space)
            for model_indexer_i, pair in enumerate(space.get_indexers().items()):
                model, indexers = pair
                print "  %s.%s: `%s`" % (space_i, model_indexer_i, utils.model_name(model))
                for indexer_i, indexer in enumerate(indexers):
                    print "    %s.%s.%s: `%s`" % (space_i, model_indexer_i, indexer_i, indexer)

    def do_exit(self, arg):
        """
        Exit shell
        """
        return True

    def do_use(self, index):
        """
        Changes current index
        """
        space, model, indexer = self._get_indexer(index)

        self._current_index = indexer

        print "Using `%s:%s:%s` index." % (space, utils.model_name(model), indexer)

    def do_usecomposite(self, indexes):
        """
        Changes current index to composition of given indexers
        """
        from djapian.indexer import CompositeIndexer

        indexers = []
        for index in indexes.split(' '):
            indexers.append(self._get_indexer(index.strip()))

        self._current_index = CompositeIndexer(*[i[2] for i in indexers])

        print "Using composition of:"
        for indexer in indexers:
            space, model, indexer = indexer
            print "  `%s:%s:%s`" % (space, utils.model_name(model), indexer)
        print "indexes."

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

        start, end = self._parse_slice(slice, default=(1, db.get_lastdocid()))

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

    def _get_indexer(self, index):
        space, model, indexer = self._parse_slice(index, '.')

        space = IndexSpace.instances[space]
        model = space.get_indexers().keys()[model]
        indexer = space.get_indexers()[model][indexer]

        return space, model, indexer

    def _parse_slice(self, slice="", delimeter=":", default=tuple()):
        if slice:
            bits = map(int, slice.split(delimeter))
        elif default:
            return default
        else:
            raise ValueError("Empty slice")

        return bits

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
