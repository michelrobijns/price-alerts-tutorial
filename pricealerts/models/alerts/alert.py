import uuid
import requests
import pricealerts.models.alerts.constants as AlertConstants
import datetime
from pricealerts.common.database import Database
from pricealerts.models.items.item import Item
from pricealerts import app


class Alert(object):
    def __init__(self, user_email, price_limit, item_id, active=True, last_checked=None, _id=None):
        self.user_email = user_email
        self.price_limit = price_limit
        self.item = Item.get_by_id(item_id)
        self.active = active
        self.last_checked = datetime.datetime.utcnow() if last_checked is None else last_checked
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return '<Alert for {} on {} with price {}>'.format(self.user_email, self.item.name, self.price_limit)

    def send(self):
        return requests.post(
            app.config['MAILGUN_URL'],
            auth=("api", app.config['MAILGUN_API_KEY']),
            data={
                "from": app.config['MAILGUN_FROM'],
                "to": self.user_email,
                "subject": "Price limit reached for {}".format(self.item.name),
                "text": "We've found a deal! ({})\nTo see the alert, visit {}.".format(
                    self.item.url, "http://<url>/alerts/{}".format(self._id))
            }
        )

    @classmethod
    def find_needing_update(cls, minutes_since_update=AlertConstants.ALERT_TIMEOUT):
        last_updated_limit = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes_since_update)

        cursor = Database.CONN.execute("select * from {} where last_checked<=? and active=1".format(AlertConstants.COLLECTION),
                                       (last_updated_limit,))
        alerts = cursor.fetchall()
        return [cls(*alert) for alert in alerts]

    def save_to_db(self):
        Database.CONN.execute('insert or replace into {} values (?, ?, ?, ?, ?, ?)'.format(AlertConstants.COLLECTION),
                              (self.user_email, self.price_limit, self.item._id, self.active,
                               self.last_checked, self._id))
        Database.CONN.commit()

    def load_item_price(self):
        self.item.load_price()
        self.last_checked = datetime.datetime.utcnow()
        self.item.save_to_db()
        self.save_to_db()
        return self.item.price

    def send_email_if_price_reached(self):
        if self.item.price < self.price_limit:
            self.send()

    @classmethod
    def find_by_user_email(cls, user_email):
        cursor = Database.CONN.execute('select * from {} where user_email = ?'.format(AlertConstants.COLLECTION),
                                       (user_email,))
        alerts = cursor.fetchall()
        return [cls(*alert) for alert in alerts]

    @classmethod
    def find_by_id(cls, _id):
        cursor = Database.CONN.execute('select * from {} where _id = ?'.format(AlertConstants.COLLECTION), (_id,))
        alert_data = cursor.fetchone()
        if alert_data is not None:
            return cls(*alert_data)

    def activate(self):
        self.active = True
        self.save_to_db()

    def deactivate(self):
        self.active = False
        self.save_to_db()

    def delete(self):
        Database.CONN.execute('delete from {} where _id = ?'.format(AlertConstants.COLLECTION), (self._id,))
