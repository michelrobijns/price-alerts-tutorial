import sqlite3
from pricealerts import app


class Database(object):
    DATABASE = app.config['DATABASE_FILE']
    CONN = None

    @staticmethod
    def initialize():
        Database.CONN = sqlite3.connect(Database.DATABASE, check_same_thread=False)

        Database.CONN.execute('create table if not exists users (email text, password text, _id text unique)')
        Database.CONN.execute('create table if not exists items (name text, url text, price real, _id text unique)')
        Database.CONN.execute('create table if not exists stores (name text, url_prefix text, tag_name text,'
                              ' query blob, _id text unique)')
        Database.CONN.execute('create table if not exists alerts (user_email text, price_limit real, item_id text,'
                              ' active integer, last_checked text, _id text unique)')
