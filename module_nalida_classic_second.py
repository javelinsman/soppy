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

from module import Module

import bot_config

class ModuleNalidaClassicSecond(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.key_set_registered_users = 'set-registered-users'

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key_set_registered_users, context["author_id"])

    def filter(self, message):
        context = message["context"]
        return any((
            context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN,
            self.membership_test(context),
            ))

    def operator(self, message):
        context = message["context"]
        if context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN:
            message["data"]["text"] = "What's up, master?"
            self.send(message)
        elif self.membership_test(message["context"]):
            message["data"]["text"] = "I know you"
            self.send(message)
        else:
            logging.error('This clause should never be executed!')
