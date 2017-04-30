import uuid
from pricealerts.common.database import Database
import pricealerts.models.stores.constants as StoreConstants
import json
import pricealerts.models.stores.errors as StoreErrors


class Store(object):
    def __init__(self, name, url_prefix, tag_name, query, _id=None):
        self.name = name
        self.url_prefix = url_prefix
        self.tag_name = tag_name

        # <query> is supplied as a string when class methods are called because the query is stored as json in the
        # sqlite3 database.
        if isinstance(query, str):
            self.query = json.loads(query)
        else:
            self.query = query

        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return '<Store {}>'.format(self.name)

    @classmethod
    def get_by_id(cls, _id):
        cursor = Database.CONN.execute('select * from {} where _id = ?'.format(StoreConstants.COLLECTION), (_id,))
        store_data = cursor.fetchone()
        if store_data is not None:
            return cls(*store_data)

    def save_to_db(self):
        Database.CONN.execute('insert or replace into {} values (?, ?, ?, ?, ?)'.format(StoreConstants.COLLECTION),
                              (self.name, self.url_prefix, self.tag_name, json.dumps(self.query), self._id))
        Database.CONN.commit()

    @classmethod
    def get_by_name(cls, store_name):
        cursor = Database.CONN.execute('select * from {} where name = ?'.format(StoreConstants.COLLECTION),
                                       (store_name,))
        store_data = cursor.fetchone()
        if store_data is not None:
            return cls(*store_data)

    @classmethod
    def get_by_url_prefix(cls, url_prefix):
        cursor = Database.CONN.execute('select * from {} where url_prefix like ?'.format(StoreConstants.COLLECTION),
                                       ('%' + str(url_prefix) + '%',))
        store_data = cursor.fetchone()
        if store_data is not None:
            return cls(*store_data)

    @classmethod
    def find_by_url(cls, url):
        """
        Return a store from a url
        :param url: The item's url
        :return: a Store, or raises a StoreNotFoundException if no store matches the url
        """
        for i in range(0, len(url)):
            try:
                store = cls.get_by_url_prefix(url[:i+1])
                return store
            except:
                raise StoreErrors.StoreNotFoundException("The URL prefix didn't yield any results")

    @classmethod
    def all(cls):
        cursor = Database.CONN.execute('select * from {}'.format(StoreConstants.COLLECTION))
        store_data = cursor.fetchall()
        return [cls(*store) for store in store_data]

    def delete(self):
        Database.CONN.execute('delete from {} where _id = ?'.format(StoreConstants.COLLECTION), (self._id,))

