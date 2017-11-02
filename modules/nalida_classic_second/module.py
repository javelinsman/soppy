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


from modules.nalida_classic_second import string_resources as sr
from basic.module import Module

import bot_config

class ModuleNalidaClassicSecond(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.key_set_registered_users = 'set-registered-users'
        self.key_set_registration_keys = 'set-registration-keys'
        self.key_context_state = 'key-context-state:%s'
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

    def set_state(self, context, state):
        "set user(context)'s state"
        serialized = self.serialize_context(context)
        state_key = self.key_context_state % serialized
        self.db.set(state_key, state)

    def get_state(self, context):
        "get user(context)'s state"
        serialized = self.serialize_context(context)
        state_key = self.key_context_state % serialized
        result = self.db.get(state_key)
        result = None if result == '' else result
        return result

    def filter(self, message):
        context = message["context"]
        return any((
            context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN,
            self.membership_test(context),
            message["type"] == 'text' and self.is_registration_key(message["data"]["text"]),
            #message["type"] == 'tick',
            ))

    def state_asked_nick(self, message):
        "response should be their wanted nickname"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.send_text(context, sr.CONFIRM_NICKNAME % text)
            self.db.set('candidate-nickname', text)
            self.set_state(context, 'asked_nick_confirmation')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_nick_confirmation(self, message):
        """response should be YES or NO depending on whether the nickname is
           submitted correctly"""
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            if text == sr.RESPONSE_NICKNAME_YES:
                nickname = self.db.get('candidate-nickname')
                self.send_text(context, sr.NICKNAME_SUBMITTED % nickname)
                self.send_text(context, sr.ASK_EXPLANATION_FOR_NICKNAME)
                self.set_state(context, 'asked_nick_explanation')
            elif text == sr.RESPONSE_NICKNAME_NO:
                self.send_text(context, sr.ASK_NICKNAME_AGAIN)
                self.set_state(context, 'asked_nick')
            else:
                self.send_text(context, sr.WRONG_RESPONSE_FORMAT)
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_nick_explanation(self, message):
        "response should be the explanation in one message"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.send_text(context, sr.EXPLANATION_SUBMITTED)
            self.send_text(context, sr.ASK_GOAL)
            self.set_state(context, 'asked_goal')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_goal(self, message):
        "response should be the description of the goal in one message"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.send_text(context, sr.GOAL_SUBMITTED)
            self.send_text(context, sr.INSTRUCTIONS_FOR_GOAL)
            self.send_text(context, sr.INSTRUCTIONS_FOR_EMOREC)
            self.set_state(context, '')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def operator(self, message):
        context = message["context"]
        if context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN:
            if message["type"] == 'text':
                text = message["data"]["text"]
                if text == sr.COMMAND_PUBLISH_REGISTRATION_KEY:
                    self.send_text(context, self.generate_new_registration_key())
        elif self.membership_test(context):
            state = self.get_state(context)
            if state is not None:
                getattr(self, 'state_' + state)(message)
            else:
                self.send_text(context, 'meow')

        elif message["type"] == 'text' and self.is_registration_key(message["data"]["text"]):
            self.register_user(context, message["data"]["text"])
            self.send_text(context, sr.REGISTER_COMPLETE)
            self.send_text(context, sr.ASK_NICKNAME)
            self.set_state(context, 'asked_nick')
        else:
            logging.error('This clause should never be executed!')
