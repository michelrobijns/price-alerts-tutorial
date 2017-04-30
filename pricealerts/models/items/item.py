from bs4 import BeautifulSoup
import requests
import re
from pricealerts.common.database import Database
import pricealerts.models.items.constants as ItemsConstants
import uuid
from pricealerts.models.stores.store import Store


class Item(object):
    def __init__(self, name, url, price=None, _id=None):
        self.name = name
        self.url = url
        store = Store.find_by_url(url)
        self.tag_name = store.tag_name
        self.query = store.query
        self.price = None if price is None else price
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return '<Item {} with URL {}>'.format(self.name, self.url)

    def load_price(self):
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content, "html.parser")
        element = soup.find(self.tag_name, self.query)
        string_price = element.text.strip()

        pattern = re.compile("(\d+.\d+)")
        match = pattern.search(string_price)

        self.price = float(match.group())
        return self.price

    def save_to_db(self):
        Database.CONN.execute('insert or replace into {} values (?, ?, ?, ?)'.format(ItemsConstants.COLLECTION),
                              (self.name, self.url, self.price, self._id))
        Database.CONN.commit()

    @classmethod
    def from_db(cls, _id):
        cursor = Database.CONN.execute('select * from {} where _id = ?'.format(ItemsConstants.COLLECTION), (_id,))
        item_data = cursor.fetchone()
        if item_data is not None:
            return cls(*item_data)

    @classmethod
    def get_by_id(cls, item_id):
        cursor = Database.CONN.execute('select * from {} where _id = ?'.format(ItemsConstants.COLLECTION),
                                       (item_id,))
        item_data = cursor.fetchone()
        if item_data is not None:
            return cls(*item_data)
