import xapian

from django.db.models import get_model

from djapian import utils

class defaultdict(dict):
    def __init__(self, value_type):
        self._value_type= value_type

    def __getitem__(self, key):
        if key not in self:
            dict.__setitem__(self, key, list())
        return dict.__getitem__(self, key)

class ResultSet(object):
    def __init__(self, indexer, query_str, offset=0, limit=utils.DEFAULT_MAX_RESULTS,
                 order_by=None, prefetch=False, flags=None):
        self._indexer = indexer
        self._query_str = query_str
        self._offset = offset
        self._limit = limit
        self._order_by = order_by
        self._prefetch = prefetch

        if flags is None:
            flags = xapian.QueryParser.FLAG_PHRASE\
                        | xapian.QueryParser.FLAG_BOOLEAN\
                        | xapian.QueryParser.FLAG_LOVEHATE
        self._flags = flags

        self._resultset_cache = None
        self._mset = None
        self._query = None
        self._query_parser = None

    def spell_correction(self):
        return self._clone(
            flags=self._flags | xapian.QueryParser.FLAG_SPELLING_CORRECTION\
                                | xapian.QueryParser.FLAG_WILDCARD
        )

    def prefetch(self):
        return self._clone(prefetch=True)

    def order_by(self, field):
        return self._clone(order_by=field)

    def flags(self, flags):
        return self._clone(flags=flags)

    #def stemming(self, lang):
    #    return self._clone(stemming_lang=lang)

    def count(self):
        return self._clone()._do_count()

    def get_corrected_query_string(self):
        self._fetch_results()
        return self._query_parser.get_corrected_query_string()

    def _clone(self, **kwargs):
        data = {
            "indexer": self._indexer,
            "query_str": self._query_str,
            "offset": self._offset,
            "limit": self._limit,
            "order_by": self._order_by,
            "prefetch": self._prefetch,
            "flags": self._flags
        }
        keys = data.keys()

        data.update(kwargs)

        return ResultSet(**data)

    def _do_count(self):
        self._fetch_results()

        return self._mset.size()

    def _do_prefetch(self):
        model_map = defaultdict(list)

        for hit in self._resultset_cache:
            model_map[hit.model].append(hit)

        for model, hits in model_map.iteritems():
            pks = [hit.pk for hit in hits]

            instances = model._default_manager.in_bulk(pks)

            for hit in hits:
                hit.instance = instances[hit.pk]

    def _fetch_results(self):
        if self._resultset_cache is None:
            self._mset, self._query, self._query_parser = self._indexer._do_search(
                self._query_str,
                self._offset,
                self._limit,
                self._order_by,
                self._flags
            )
            self._parse_results()

        return self._resultset_cache

    def _parse_results(self):
        self._resultset_cache = []

        for match in self._mset:
            doc = match.get_document()

            model = doc.get_value(2)
            model = get_model(*model.split('.'))
            pk = model._meta.pk.to_python(doc.get_value(1))

            percent = match.get_percent()
            rank = match.get_rank()
            weight = match.get_weight()

            self._resultset_cache.append(Hit(pk, model, percent, rank, weight))

        if self._prefetch:
            self._do_prefetch()

    def __iter__(self):
        self._fetch_results()
        return iter(self._resultset_cache)

    def __len__(self):
        self._fetch_results()
        return len(self._resultset_cache)

    def __getitem__(self, k):
        if not isinstance(k, (slice, int, long)):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0))
                or (isinstance(k, slice) and (k.start is None or k.start >= 0)
                    and (k.stop is None or k.stop >= 0))), \
                "Negative indexing is not supported."

        if self._resultset_cache is not None:
            return self._fetch_results()[k]
        else:
            if isinstance(k, slice):
                start, stop = k.start, k.stop
                if start is None:
                    start = 0
                if stop is None:
                    kstop = utils.DEFAULT_MAX_RESULTS

                return self._clone(
                    offset=start,
                    limit=stop - start
                )
            else:
                return list(self._clone(
                    offset=k,
                    limit=1
                ))[k]

        def __unicode__(self):
            return "<ResultSet: query=%s prefetch=%s>" % (self.query_str, self._prefetch)

class Hit(object):
    def __init__(self, pk, model, percent, rank, weight):
        self.pk = pk
        self.model = model
        self.percent = percent
        self.rank = rank
        self.weight = weight
        self._instance = None

    def get_instance(self):
        if self._instance is None:
            self._instance = self.model._default_manager.get(pk=self.pk)
        return self._instance

    def set_instance(self, instance):
        self._instance = instance

    instance = property(get_instance, set_instance)

    def __repr__(self):
        return "<Hit: model=%s pk=%s, percent=%s rank=%s weight=%s>" % (
            utils.model_name(self.model), self.pk, self.percent, self.rank, self.weight
        )
