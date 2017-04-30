import sqlite3


class Database(object):
    DATABASE = '/var/www/pricealerts/pricealerts/database/database.db'
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

# class Database(object):
#     URI = "mongodb://127.0.0.1:27017"
#     DATABASE = None
#
#     @staticmethod
#     def initialize():
#         client = pymongo.MongoClient(Database.URI)
#         Database.DATABASE = client['fullstack']
#
#     @staticmethod
#     def insert(collection, data):
#         Database.DATABASE[collection].insert(data)
#
#     @staticmethod
#     def find(collection, query):
#         return Database.DATABASE[collection].find(query)
#
#     @staticmethod
#     def find_one(collection, query):
#         return Database.DATABASE[collection].find_one(query)
