import datetime
import os

from django.db import models
from django.utils.itercompat import is_iterable
from djapian.signals import post_save, pre_delete
from django.conf import settings
from django.utils.encoding import smart_unicode

from djapian.resultset import ResultSet
from djapian import utils

import xapian

class Field(object):
    raw_types = (int, long, float, basestring, bool, models.Model,
                 datetime.time, datetime.date, datetime.datetime)

    def __init__(self, path, weight=utils.DEFAULT_WEIGHT, prefix=""):
        self.path = path
        self.weight = weight
        self.prefix = prefix

    def get_tag(self):
        return self.prefix.upper()

    def resolve(self, value):
        bits = self.path.split(".")

        for bit in bits:
            try:
                value = getattr(value, bit)
            except AttributeError:
                raise

            if callable(value):
                try:
                    value = value()
                except TypeError:
                    raise

        if isinstance(value, self.raw_types):
            return value
        elif is_iterable(value):
            return ", ".join(value)
        elif isinstance(value, models.Manager):
            return ", ".join(value.all())
        return None

class Indexer(object):
    field_class = Field
    free_values_start_number = 11

    fields = []
    tags = []
    aliases = {}
    trigger = lambda indexer, obj: True
    stemming_lang_accessor = None

    def __init__(self, db, model):
        """
        Initialize an Indexer whose index data to `db`.
        `model` is the Model whose instances will be used as documents.
        Note that fields from other models can still be used in the index,
        but this model will be the one returned from search results.
        """
        self._db = db
        self._model = model
        self._model_name = ".".join([model._meta.app_label, model._meta.object_name.lower()])

        self.fields = [] # Simple text fields
        self.tags = [] # Prefixed fields
        self.aliases = {}

        #
        # Parse fields
        # For each field checks if it is a tuple or a list and add it's
        # weight
        #
        for field in self.__class__.fields:
            if isinstance(field, (tuple, list)):
                self.fields.append(Field(field[0], field[1]))
            else:
                self.fields.append(Field(field))

        #
        # Parse prefixed fields
        #
        for field in self.__class__.tags:
            tag, path = field[:2]
            if len(field) == 3:
                weight = field[2]
            else:
                weight = utils.DEFAULT_WEIGHT

            self.tags.append(Field(path, weight, prefix=tag))

        for tag, aliases in self.__class__.aliases.iteritems():
            if self.has_tag(tag):
                if not isinstance(aliases, (list, tuple)):
                    aliases = (aliases,)
                self.aliases[tag] = aliases
            else:
                raise ValueError("Cannot create alias for tag `%s` that doesn't exist" % tag)

        models.signals.post_save.connect(post_save, sender=self._model)
        models.signals.pre_delete.connect(pre_delete, sender=self._model)

    def __unicode__(self):
        return self.__class__.get_descriptor()
    __str__ = __unicode__

    def has_tag(self, name):
        for field in self.tags:
            if field.prefix == name:
                return True

        return False

    def tag_index(self, name):
        for i, field in enumerate(self.tags):
            if field.prefix == name:
                return i

        return None

    @classmethod
    def get_descriptor(cls):
        return ".".join([cls.__module__, cls.__name__]).lower()

    # Public Indexer interface

    def update(self, documents=None, after_index=None):
        """
        Update the database with the documents.
        There are some default value and terms in a document:
         * Values:
           1. Used to store the ID of the document
           2. Store the model of the object (in the string format, like
              "project.app.model")
           3. Store the indexer descriptor (module path)
           4..10. Free

         * Terms
           UID: Used to store the ID of the document, so we can replace
                the document by the ID
        """
        # Open Xapian Database
        database = self._db.open(write=True)

        # If doesnt have any document get all
        if documents is None:
            update_queue = self._model.objects.all()
        else:
            update_queue = documents

        try:
            iterator = update_queue.iterator()
        except AttributeError:
            iterator = iter(update_queue)

        # Get each document received
        for obj in iterator:
            if not self.trigger(obj):
                self.delete(obj.pk, database)
                continue

            doc = xapian.Document()
            #
            # Add default terms and values
            #
            uid = self._create_uid(obj)
            doc.add_term(self._create_uid(obj))
            self._insert_meta_values(doc, obj)

            generator = xapian.TermGenerator()
            generator.set_database(database)
            generator.set_document(doc)
            generator.set_flags(xapian.TermGenerator.FLAG_SPELLING)

            stem_lang = self._get_stem_language(obj)
            if stem_lang:
                generator.set_stemmer(xapian.Stem(stem_lang))

            valueno = self.free_values_start_number

            for field in self.fields + self.tags:
                # Trying to resolve field value or skip it
                try:
                    value = field.resolve(obj)
                except AttributeError:
                    if field.prefix:
                        valueno += 1

                if field.prefix:
                    # If it is a model field make some postprocessing of its value
                    try:
                        content_type = self._model._meta.get_field(field.path.split('.')[0])
                    except models.FieldDoesNotExist:
                        content_type = value

                    index_value = self._get_index_value(value, content_type)
                    if index_value is not None:
                        doc.add_value(valueno, smart_unicode(index_value))
                    valueno += 1
                prefix = smart_unicode(field.get_tag())
                generator.index_text(smart_unicode(value), field.weight, prefix)
                if prefix:  # if prefixed then also index without prefix
                    generator.index_text(smart_unicode(value), field.weight)

            database.replace_document(uid, doc)
            #FIXME: ^ may raise InvalidArgumentError when word in
            #         text larger than 255 simbols
            if after_index:
                after_index(obj)
        database.flush()
        del database

    def search(self, query):
        return ResultSet(self, query)

    def delete(self, obj, database=None):
        """
        Delete a document from index
        """
        try:
            if database is None:
                database = self._db.open(write=True)
            database.delete_document(self._create_uid(obj))
        except (IOError, RuntimeError, xapian.DocNotFoundError), e:
            pass

    def document_count(self):
        database = self._db.open()
        return database.get_doccount()

    __len__ = document_count

    def clear(self):
        self._db.clear()

    # Private Indexer interface

    def _get_meta_values(self, obj):
        if isinstance(obj, models.Model):
            pk = obj.pk
        else:
            pk = obj
        return [pk, self._model_name, self.__class__.get_descriptor()]

    def _insert_meta_values(self, doc, obj, start=1):
        for value in self._get_meta_values(obj):
            doc.add_value(start, smart_unicode(value))
            start += 1
        return start

    def _create_uid(self, obj):
        """
        Generates document UID for given object
        """
        return "UID-" + "-".join(map(smart_unicode, self._get_meta_values(obj)))

    def _do_search(self, query, offset, limit, order_by, flags):
        """
        flags are as defined in the Xapian API :
        http://www.xapian.org/docs/apidoc/html/classXapian_1_1QueryParser.html
        Combine multiple values with bitwise-or (|).
        """
        database = self._db.open()
        enquire = xapian.Enquire(database)

        if order_by in (None, 'RELEVANCE'):
            enquire.set_sort_by_relevance()
        else:
            ascending = True
            if order_by.startswith('-'):
                ascending = False

            if order_by[0] in '+-':
                order_by = order_by[1:]

            try:
                valueno = self.free_values_start_number + self.tag_index(order_by)
            except (ValueError, TypeError):
                raise ValueError("Field %s cannot be used in order_by clause"
                                 " because it doen't exist in index" % order_by)

            enquire.set_sort_by_relevance_then_value(valueno, ascending)

        query, query_parser = self._parse_query(query, database, flags)
        enquire.set_query(
            query
        )

        return enquire.get_mset(offset, limit), query, query_parser

    def _get_stem_language(self, obj=None):
        """
        Returns stemmig language for given object if acceptable or model wise
        """
        language = getattr(settings, "DJAPIAN_STEMMING_LANG", "none") # Use the language defined in DJAPIAN_STEMMING_LANG

        if obj:
            try:
                language = Field(self.stemming_lang_accessor).resolve(obj)
            except AttributeError:
                pass

        return language

    def _get_index_value(self, field_value, content_type):
        """
        Generates index values (for sorting) for given field value and its content type
        """
        value = field_value

        if isinstance(content_type, (models.IntegerField, int, long)):
            #
            # Integer fields are stored with 12 leading zeros
            #
            value = '%012d' % field_value
        elif isinstance(content_type, (models.BooleanField, bool)):
            #
            # Boolean fields are stored as 't' or 'f'
            #
            if field_value:
                value = 't'
            else:
                value = 'f'
        elif isinstance(content_type, (models.DateTimeField, datetime.datetime)):
            #
            # DateTime fields are stored as %Y%m%d%H%M%S (better
            # sorting)
            #
            value = field_value.strftime('%Y%m%d%H%M%S')

        return value

    def _parse_query(self, term, db, flags):
        """
        Parses search queries
        """
        # Instance Xapian Query Parser
        query_parser = xapian.QueryParser()

        for field in self.tags:
            query_parser.add_prefix(field.prefix.lower(), field.get_tag())
            if field.prefix in self.aliases:
                for alias in self.aliases[field.prefix]:
                    query_parser.add_prefix(alias, field.get_tag())

        query_parser.set_database(db)
        query_parser.set_default_op(xapian.Query.OP_AND)

        stemming_lang = self._get_stem_language()
        if stemming_lang:
            query_parser.set_stemmer(xapian.Stem(stemming_lang))
            query_parser.set_stemming_strategy(xapian.QueryParser.STEM_SOME)

        parsed_query = query_parser.parse_query(term, flags)

        return parsed_query, query_parser
