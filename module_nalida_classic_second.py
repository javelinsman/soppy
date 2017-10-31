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

import bot_config

class ModuleNalidaClassicSecond(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.key_set_registered_users = 'set-registered-users'
        self.key_set_registration_keys = 'set-registration-keys'

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key_set_registered_users, context["author_id"])

    def generate_new_registration_key(self):
        "make new key, insert to db, and return it"
        while True:
            new_key = '%s:%s' % (
                self.module_name,
                ''.join([random.choice(string.ascii_letters) for _ in range(25)])
                )
            if not self.db.sismember(self.key_set_registration_keys, new_key):
                break
        self.db.sadd(self.key_set_registration_keys, new_key)
        return new_key

    def filter(self, message):
        context = message["context"]
        return any((
            context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN,
            self.membership_test(context),
            message["type"] == 'text' and
            self.db.sismember(self.key_set_registration_keys, message["data"]["text"]),
            ))

    def operator(self, message):
        context = message["context"]
        if context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN:
            message["data"]["text"] = self.generate_new_registration_key()
            self.send(message)
        if message["type"] == 'text' and \
           self.db.sismember(self.key_set_registration_keys, message["data"]["text"]):
            message["data"]["text"] = "You'll be registered as a user"
            self.send(message)
        elif self.membership_test(message["context"]):
            message["data"]["text"] = "I know you"
            self.send(message)
        else:
            logging.error('This clause should never be executed!')
