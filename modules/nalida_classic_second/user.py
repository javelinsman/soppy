"manages user informations for nalida classic 2nd"

import logging
import json
import random
import string

from basic.module import Module

class User:
    "mainly about getters and setters"
    def __init__(self, db):
        self.db = db #pylint: disable=invalid-name
        self.key = {
            "nickname": 'user-key-nickname:%s',
            "goal": 'user-goal:%s',
            "explanation": 'user-explanation:%s',
            "session": 'user-session:%s',
            "state": 'user-state:%s',
            "emorec_time": 'user-emorec-time:%s',
            "registered_users": 'user-registered-users',
            "registration_keys": 'user-registration-keys',
            }

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key["registered_users"], Module.serialize_context(context))

    def register_user(self, context, registration_key):
        "register the context as a user of this module"
        self.db.sadd(self.key["registered_users"], Module.serialize_context(context))
        self.db.srem(self.key["registration_keys"], registration_key)

    def generate_new_registration_key(self):
        "make new key, insert to db, and return it"
        while True:
            new_key = '%s:%s' % (
                'Nalida-Classic-Second',
                ''.join([random.choice(string.ascii_letters) for _ in range(25)])
                )
            if not self.is_registration_key(new_key):
                break
        self.db.sadd(self.key["registration_keys"], new_key)
        return new_key

    def is_registration_key(self, key):
        "check if the key is the registration key"
        return self.db.sismember(self.key["registration_keys"], key)

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

    def goal(self, context, value=None):
        "getset of goal"
        serialized = Module.serialize_context(context)
        key = self.key["goal"] % serialized
        if value is None:
            return self.db.get(key)
        else:
            self.db.set(key, value)

    def explanation(self, context, value=None):
        "getset of explanation"
        serialized = Module.serialize_context(context)
        key = self.key["explanation"] % serialized
        if value is None:
            return self.db.get(key)
        else:
            self.db.set(key, value)

    def session(self, context, value=None):
        "getset of session"
        serialized = Module.serialize_context(context)
        key = self.key["session"] % serialized
        if value is None:
            logging.debug('context is %s, session get returns %s',
                          serialized, self.db.get(key))
            return self.db.get(key)
        else:
            logging.debug('context is %s, session set to %s', serialized, value)
            self.db.set(key, value)

    def emorec_time(self, context, set_value=None):
        "get/set of current/next emorec time"
        serialized = Module.serialize_context(context)
        key = self.key["emorec_time"] % serialized
        if set_value is None:
            return json.loads(self.db.get(key))
        else:
            if set_value == 'morning':
                hour = random.randint(8, 9)
            elif set_value == 'noon':
                hour = random.randint(14, 15)
            elif set_value == 'night':
                hour = random.randint(20, 21)
            else:
                return None
            minute = random.randint(0, 59)
            self.db.set(key, json.dumps([hour, minute]))
            return [hour, minute]
