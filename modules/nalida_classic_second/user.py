"manages user informations for nalida classic 2nd"

import logging
import json
import random
import string
import time

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
            "emorec_block": 'user-emorec-block:%s',
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

    def list_of_users(self):
        "returns the list of registrated users"
        users = self.db.smembers(self.key["registered_users"])
        return list(map(Module.parse_context, users))

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

    def emorec_time(self, context, set_next=False):
        "get/set of current/next emorec time"
        serialized = Module.serialize_context(context)
        key = self.key["emorec_time"] % serialized
        result = self.db.get(key)
        result = json.loads(result) if result is not None else result
        if set_next:
            minute = random.randint(0, 59)
            if result is None:
                current = time.localtime()
                hour = current.tm_hour
                minute = current.tm_min
                if hour <= 9:
                    when = 'morning'
                elif hour <= 15:
                    when = 'noon'
                else:
                    when = 'night'
                self.db.set(key, json.dumps([when, hour, minute]))
            elif result[0] == 'night':
                hour = random.randint(8, 9)
                self.db.set(key, json.dumps(['morning', hour, minute]))
            elif result[0] == 'morning':
                hour = random.randint(14, 15)
                self.db.set(key, json.dumps(['noon', hour, minute]))
            elif result[0] == 'noon':
                hour = random.randint(20, 21)
                self.db.set(key, json.dumps(['night', hour, minute]))
        else:
            if result is None:
                return [-1, -1]
            return result[1:]

    def emorec_block(self, context, block=False):
        "if the user is blocked for emorec response"
        serialized = Module.serialize_context(context)
        key = self.key["emorec_block"] % serialized
        if block:
            self.db.set(key, 1)
            self.db.expire(key, 30 * 60)
        else:
            return self.db.get(key) is not None
