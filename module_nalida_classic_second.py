"""
Module for Nalida Classic: 2nd
This module contains
    - registration routine
    - interface to the emotion recording module
        & sharing public responses
    - interface to the goal achievement module
    - team notification
"""

import logging
import string
import random

from module import Module
from string_data import StringData

import bot_config

class ModuleNalidaClassicSecond(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.key_set_registered_users = 'set-registered-users'
        self.key_set_registration_keys = 'set-registration-keys'
        self.string_data = StringData()
    
    def get_string(self, name):
        key = '%s:%s' % (self.module_name, name)
        return self.string_data.get(key)

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key_set_registered_users, self.serialize_context(context))

    def is_registration_key(self, key):
        "check if the key is the registration key"
        return self.db.sismember(self.key_set_registration_keys, key)

    def register_user(self, context, registration_key):
        "register the context as a user of this module"
        self.db.sadd(self.key_set_registered_users, self.serialize_context(context))
        self.db.srem(self.key_set_registration_keys, registration_key)

    def generate_new_registration_key(self):
        "make new key, insert to db, and return it"
        while True:
            new_key = '%s:%s' % (
                self.module_name,
                ''.join([random.choice(string.ascii_letters) for _ in range(25)])
                )
            if not self.is_registration_key(new_key):
                break
        self.db.sadd(self.key_set_registration_keys, new_key)
        return new_key

    def filter(self, message):
        context = message["context"]
        return any((
            context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN,
            self.membership_test(context),
            message["type"] == 'text' and self.is_registration_key(message["data"]["text"]),
            ))

    def operator(self, message):
        context = message["context"]
        if context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN:
            self.send_text(context, self.generate_new_registration_key())
        if message["type"] == 'text' and self.is_registration_key(message["data"]["text"]):
            self.register_user(context, message["data"]["text"])
            self.send_text(context, self.get_string('REGISTER_COMPLETE'))
        elif self.membership_test(context):
            self.send_text(context, "I know you")
        else:
            logging.error('This clause should never be executed!')
