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
import json
import datetime
import random


from modules.soppy import string_resources as sr
from modules.soppy.user import User
from modules.soppy.session import Session
from basic.module import Module

import bot_config

class ModuleSoppy(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.user = User(self)
        self.session = Session(self)
        self.key = {
            "list_goal_achievement": 'key-list-goal-achievement:%s',
            "list_emorec_response": 'key-emorec-response:%s',
            "temp_goal_response": 'key-temp-goal-response:%s',
            }

    def send_text(self, context, text, interface_name):
        for subtext in text.split('$$$'):
            super().send_text(context, subtext, interface_name)

    def filter(self, message):
        context = message["context"]
        return message["type"] == 'text'

    def state_asked_nick(self, message):
        "response should be their wanted nickname"
        context = message["context"]
        text = message["data"]["text"]
        self.send_text(context, sr.CONFIRM_NICKNAME % text, message["from"])
        serialized = self.serialize_context(context)
        self.db.set('candidate-nickname:%s' % serialized, text)
        self.user.state(context, 'asked_nick_confirmation')

    def state_asked_nick_confirmation(self, message):
        """response should be YES or NO depending on whether the nickname is
           submitted correctly"""
        context = message["context"]
        text = message["data"]["text"]
        if text == sr.RESPONSE_NICKNAME_YES:
            serialized = self.serialize_context(context)
            nickname = self.db.get('candidate-nickname:%s' % serialized)
            self.user.nick(context, nickname)
            self.send_text(context, sr.OKAY_WHATS_YOUR_TROUBLE % nickname, message["from"])
            self.user.state(context, 'asked_trouble')
        elif text == sr.RESPONSE_NICKNAME_NO:
            self.send_text(context, sr.ASK_NICKNAME_AGAIN, message["from"])
            self.user.state(context, 'asked_nick')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT, message["from"])

    def state_asked_trouble(self, message):
        context = message["context"]
        self.send_text(context, sr.DETAILED_EXPLANATION, message["from"])
        self.user.state(context, 'asked_detail')

    def state_asked_detail(self, message):
        context = message["context"]
        self.send_text(context, sr.WHAT_DID_YOU_DO, message["from"])
        self.user.state(context, 'asked_what_did_you_do')

    def state_asked_what_did_you_do(self, message):
        context = message["context"]
        self.send_text(context, sr.DID_IT_WORK, message["from"])
        self.user.state(context, 'asked_if_it_worked')

    def state_asked_if_it_worked(self, message):
        context = message["context"]
        text = message["data"]["text"]
        if text == '네':
            self.send_text(context, sr.DID_IT_SOLVED_YOUR_PROBLEM, message["from"])
            self.user.state(context, 'asked_if_it_solved')
        elif text == '아니오':
            self.send_text(context, sr.WHY_DIDNT_IT_WORK, message["from"])
            self.user.state(context, 'asked_why_didnt_it_work')

    def state_asked_if_it_solved(self, message):
        context = message["context"]
        text = message["data"]["text"]
        if text == '네':
            self.send_text(context, sr.HOW_ABOUT_FRIENDS, message["from"])
            self.user.state(context, 'asked_about_friends')
        elif text == '아니오':
            self.send_text(context, sr.WHY_DIDNT_IT_WORK, message["from"])
            self.user.state(context, 'asked_why_didnt_it_work')

    def state_asked_why_didnt_it_work(self, message):
        context = message["context"]
        self.send_text(context, sr.TELL_ME_AGAIN, message["from"])
        self.user.state(context, 'asked_tell_me_again')

    def state_asked_tell_me_again(self, message):
        context = message["context"]
        self.send_text(context, sr.HOW_ABOUT_FRIENDS, message["from"])
        self.user.state(context, 'asked_about_friends')

    def state_asked_about_friends(self, message):
        context = message["context"]
        self.send_text(context, sr.NOW_ALL_SOLVED, message["from"])
        self.user.state(context, 'asked_now_all_solved')

    def state_asked_now_all_solved(self, message):
        context = message["context"]
        text = message["data"]["text"]
        if text == '네':
            self.send_text(context, sr.ALL_SOLVED_GOOD % self.user.nick(context), message["from"])
            self.user.state(context, '')
        elif text == '아니오':
            self.send_text(context, sr.ALL_SOLVED_BAD, message["from"])
            self.user.state(context, '')

    def execute_user_command(self, message):
        "executes commands entered in user's chat"
        context = message["context"]
        state = self.user.state(context)
        if state is None:
            self.send_text(context, sr.HELLO_YOUR_NAME, message["from"])
            self.user.state(context, 'asked_nick')
        else:
            getattr(self, 'state_' + state)(message)

    def operator(self, message):
        context = message["context"]
        self.report(message)
        if not self.user.membership_test(context):
            self.user.register_user(context)
        self.execute_user_command(message)
