from pymongo.mongo_client import MongoClient

__author__ = 'Fatman9000'


class Database(object):
    URI = "mongodb://127.0.0.1:27017"
    DATABASE = None

    @staticmethod
    def initialize():
        client = MongoClient(Database.URI)
        Database.DATABASE = client.leagueData

    @staticmethod
    def insert(data):
        Database.DATABASE['playerData'].insert(data)

    @staticmethod
    def find(query):
        return Database.DATABASE['playerData'].find(query)

    @staticmethod
    def find_one(query):
        return Database.DATABASE['playerData'].find_one(query)