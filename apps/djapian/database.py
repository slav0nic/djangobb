import os
import xapian

from django.conf import settings

class Database(object):
    def __init__(self, path):
        self._path = path

    def open(self, write=False):
        """
        Opens database for manipulations
        """
        if not os.path.exists(self._path):
            os.makedirs(self._path)

        if write:
            database = xapian.WritableDatabase(
                self._path,
                xapian.DB_CREATE_OR_OPEN,
            )
        else:
            try:
                database = xapian.Database(self._path)
            except xapian.DatabaseOpeningError:
                self.create_database()

                database = xapian.Database(self._path)

        return database

    def create_database(self):
        database = xapian.WritableDatabase(
            self._path,
            xapian.DB_CREATE_OR_OPEN,
        )
        del database

    def document_count(self):
        return self.open().get_doccount()

    def clear(self):
        try:
            for file_path in os.listdir(self._path):
                os.remove(os.path.join(self._path, file_path))

            os.rmdir(self._path)
        except OSError:
            pass

class CompositeDatabase(Database):
    def __init__(self, dbs):
        self._dbs = dbs

    def open(self, write=False):
        if write:
            raise ValueError("Composite database cannot be opened for writing")

        base = self._dbs[0]
        raw = base.open()

        for db in self._dbs[1:]:
            raw.add_database(db.open())

        return raw

    def create_database(self):
        raise NonImplementedError

    def clear(self):
        raise NotImplementedError
