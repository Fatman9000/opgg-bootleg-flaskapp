import datetime
import uuid

from flask import session

from database import Database


class User(object):
    def __init__(self, name):
        self.name = name
        
    @classmethod
    def get_by_name(cls, name):
        data = Database.find_one({"name": name})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(name):
        user = User.get_by_name(name)
        if user is not None:
            return user.name == name
        return False

    @staticmethod
    def login(name):
        session["name"] = name