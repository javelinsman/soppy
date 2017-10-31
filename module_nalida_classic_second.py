"""
Module for Nalida Classic: 2nd
This module contains
    - registration routine
    - interface to the emotion recording module
        & sharing public responses
    - interface to the goal achievement module
    - team notification
"""

from module import Module

class ModuleNalidaClassicSecond(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.key_set_registered_users = 'set-registered-users'

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key_set_registered_users, context["author_id"])

    def filter(self, message):
        return True

    def operator(self, message):
        if self.membership_test(message["context"]):
            message["data"]["text"] = "I know you"
            self.send(message)
        else:
            message["data"]["text"] = "I don't know you"
            self.send(message)
