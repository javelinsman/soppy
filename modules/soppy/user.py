"manages user informations for nalida classic 2nd"

import logging
import json
import random
import string
import time

from basic.module import Module

class User:
    "mainly about getters and setters"
    def __init__(self, parent):
        self.db = parent.db #pylint: disable=invalid-name
        self.key = {
            "nickname": 'user-key-nickname:%s',
            "state": 'user-state:%s',
            "registered_users": 'user-registered-users',
            }

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key["registered_users"], Module.serialize_context(context))

    def register_user(self, context):
        "register the context as a user of this module"
        self.db.sadd(self.key["registered_users"], Module.serialize_context(context))

    def list_of_users(self):
        "returns the list of registrated users"
        users = self.db.smembers(self.key["registered_users"])
        return list(map(Module.parse_context, users))

    def state(self, context, value=None):
        "set user(context)'s state"
        serialized = Module.serialize_context(context)
        state_key = self.key["state"] % serialized
        if value is None:
            result = self.db.get(state_key)
            return None if result == '' else result
        else:
            self.db.set(state_key, value)

    def nick(self, context, value=None):
        "getset of nick"
        serialized = Module.serialize_context(context)
        key = self.key["nickname"] % serialized
        if value is None:
            return self.db.get(key)
        else:
            self.db.set(key, value)
