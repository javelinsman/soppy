"manages user informations for nalida classic 2nd"

import logging

from basic.module import Module

class User:
    "mainly about getters and setters"
    def __init__(self, db):
        self.db = db
        self.key_nickname = 'user-key-nickname:%s'
        self.key_goal = 'user-goal:%s'
        self.key_explanation = 'user-explanation:%s'
        self.key_session = 'user-session:%s'

    def nick(self, context, value=None):
        "getset of nick"
        serialized = Module.serialize_context(context)
        key = self.key_nickname % serialized
        if value is None:
            return self.db.get(key)
        else:
            self.db.set(key, value)

    def goal(self, context, value=None):
        "getset of goal"
        serialized = Module.serialize_context(context)
        key = self.key_goal % serialized
        if value is None:
            return self.db.get(key)
        else:
            self.db.set(key, value)

    def explanation(self, context, value=None):
        "getset of explanation"
        serialized = Module.serialize_context(context)
        key = self.key_explanation % serialized
        if value is None:
            return self.db.get(key)
        else:
            self.db.set(key, value)

    def session(self, context, value=None):
        "getset of session"
        serialized = Module.serialize_context(context)
        key = self.key_session % serialized
        if value is None:
            logging.debug('context is %s, session get returns %s',
                          serialized, self.db.get(key))
            return self.db.get(key)
        else:
            logging.debug('context is %s, session set to %s', serialized, value)
            self.db.set(key, value)
