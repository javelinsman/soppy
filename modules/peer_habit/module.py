"""
Module for peer-motivational habit formation
This module contains
    - registration routine
    - goal achievement & sharing
    - team notification
"""

import logging
import random


from modules.peer_habit import string_resources as sr
from modules.peer_habit.user import User
from modules.peer_habit.session import Session
from basic.module import Module

import bot_config

class ModulePeerHabit(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.user = User(self)
        self.session = Session(self)

    def send_text(self, context, text):
        for subtext in text.split('$$$'):
            super().send_text(context, subtext)

    def report(self, text):
        "send the text to reporting room"
        self.send_text({"chat_id": bot_config.PEER_HABIT_REPORT}, text)

    def filter(self, message):
        context = message["context"]
        return any((
            context["chat_id"] == bot_config.ADMIN,
            self.user.membership_test(context),
            message["type"] == 'text' and self.user.is_registration_key(message["data"]["text"]),
            message["type"] == 'timer',
            ))

    def operator(self, message):
        context = message["context"]
        if context["chat_id"] == bot_config.ADMIN:
            self.execute_admin_command(message)
        elif self.user.membership_test(context):
            self.execute_user_command(message)
        elif message["type"] == 'text' and self.user.is_registration_key(message["data"]["text"]):
            self.user.register_user(context, message["data"]["text"])
            self.send_text(context, sr.GREETING % self.user.nick(context))
            self.send_text(context, sr.ASK_GOAL_TYPE)
            self.user.state(context, 'asked_goal_type')
        elif message["type"] == 'timer':
            self.reminder_routine(message)
        else:
            logging.error('This clause should never be executed!')

    def reminder_routine(self, message):
        "remind everyday 10, 11, 12 o'clock"
        pass

    def execute_user_command(self, message):
        "executes commands entered in user's chat"
        context = message["context"]
        state = self.user.state(context)
        if state is not None:
            getattr(self, 'state_' + state)(message)
        else:
            self.send_text(context, random.choice(sr.BOWWOWS))

    def execute_admin_command(self, message):
        "executes commands entered in the admin room"
        pass
    
    def state_asked_goal_type(self, message):
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2', '3', '4']:
            return
        self.user.goal_type(context, message["data"]["text"])
        self.send_text(context, sr.ASK_GOAL_NAME)
        self.user.state(context, 'asked_goal_name')

    def state_asked_goal_name(self, message):
        context = message["context"]
        if message["type"] != 'text':
            return
        self.user.goal_name(context, message["data"]["text"])
        self.send_text(context, sr.ASK_DIFFICULTY % self.user.nick(context))
        self.user.state(context, 'asked_difficulty')

    def state_asked_difficulty(self, message):
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2', '3', '4', '5']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.difficulty(context, message["data"]["text"])
        self.send_text(context, sr.ASK_CONSCIENTIOUSNESS)
        self.user.state(context, 'asked_conscientiousness')

    def state_asked_conscientiousness(self, message):
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2', '3', '4']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.conscientiousness(context, message["data"]["text"])
        self.send_text(context, sr.ASK_AGE % self.user.nick(context))
        self.user.state(context, 'asked_age')

    def state_asked_age(self, message):
        context = message["context"]
        if message["type"] != 'text':
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.age(context, message["data"]["text"])
        self.send_text(context, sr.ASK_SEX % self.user.nick(context))
        self.user.state(context, 'asked_sex')

    def state_asked_sex(self, message):
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.sex(context, message["data"]["text"])
        self.send_text(context, sr.ASK_PUSH_ENABLE % self.user.nick(context))
        self.user.state(context, 'asked_push_enable')

    def state_asked_push_enable(self, message):
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.push_enable(context, message["data"]["text"])
        self.report(self.user.brief_info(context))
        self.send_text(context, sr.REGISTRATION_COMPLETE)
        self.user.state(context, '')
