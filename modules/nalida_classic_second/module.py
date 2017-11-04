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


from modules.nalida_classic_second import string_resources as sr
from modules.nalida_classic_second import emorec
from modules.nalida_classic_second.user import User
from modules.nalida_classic_second.session import Session
from basic.module import Module

import bot_config

class ModuleNalidaClassicSecond(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.user = User(self.db)
        self.session = Session(self.db, self.user)
        self.key_context_state = 'key-context-state:%s'
        self.key_list_goal_achievement = 'key-list-goal-achievement:%s'
        self.key_list_emorec_response = 'key-emorec-response:%s'

    def send_text(self, context, text):
        for subtext in text.split('$$$'):
            super().send_text(context, subtext)

    def filter(self, message):
        context = message["context"]
        return any((
            context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN,
            self.user.membership_test(context),
            message["type"] == 'text' and self.user.is_registration_key(message["data"]["text"]),
            message["type"] == 'timer',
            ))

    def state_asked_nick(self, message):
        "response should be their wanted nickname"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.send_text(context, sr.CONFIRM_NICKNAME % text)
            serialized = self.serialize_context(context)
            self.db.set('candidate-nickname:%s' % serialized, text)
            self.user.state(context, 'asked_nick_confirmation')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_nick_confirmation(self, message):
        """response should be YES or NO depending on whether the nickname is
           submitted correctly"""
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            if text == sr.RESPONSE_NICKNAME_YES:
                serialized = self.serialize_context(context)
                nickname = self.db.get('candidate-nickname:%s' % serialized)
                self.user.nick(context, nickname)
                self.send_text(context, sr.NICKNAME_SUBMITTED % nickname)
                self.send_text(context, sr.ASK_EXPLANATION_FOR_NICKNAME)
                self.user.state(context, 'asked_nick_explanation')
            elif text == sr.RESPONSE_NICKNAME_NO:
                self.send_text(context, sr.ASK_NICKNAME_AGAIN)
                self.user.state(context, 'asked_nick')
            else:
                self.send_text(context, sr.WRONG_RESPONSE_FORMAT)
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_nick_explanation(self, message):
        "response should be the explanation in one message"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.user.explanation(context, text)
            self.send_text(context, sr.EXPLANATION_SUBMITTED)
            self.send_text(context, sr.ASK_GOAL)
            self.user.state(context, 'asked_goal')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_goal(self, message):
        "response should be the description of the goal in one message"

        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.user.goal(context, text)
            self.send_text(context, sr.GOAL_SUBMITTED)
            self.send_text(context, sr.INSTRUCTIONS_FOR_GOAL)
            self.send_text(context, sr.INSTRUCTIONS_FOR_EMOREC)
            self.user.emorec_time(context, True)
            self.user.state(context, '')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_emotion_detail(self, message):
        "record emotion response detail"
        context = message["context"]
        if message["type"] == 'text':
            key = self.key_list_emorec_response % self.serialize_context(context)
            text = message["data"]["text"]
            share = True
            if text.startswith(sr.COMMAND_NOT_TO_SHARE_EMOTION):
                text = text[len(sr.COMMAND_NOT_TO_SHARE_EMOTION):].strip()
                share = False
            recent_response = json.loads(self.db.lpop(key))
            recent_response[1] = message["data"]["text"]
            self.db.lpush(key, json.dumps(recent_response))
            if share:
                target_chat = self.session.target_chat(self.user.session(context))
                if target_chat is not None:
                    sharing_message = sr.EMOREC_SHARING_DETAILED_MESSAGE % text
                    self.send_text({"chat_id":target_chat}, sharing_message)
                self.send_text(context, sr.EMOREC_RESPONSE_RECORDED_AND_SHARED)
            else:
                self.send_text(context, sr.EMOREC_RESPONSE_RECORDED_BUT_NOT_SHARED)

        self.user.state(context, '')

    def state_asked_goal_detail(self, message):
        "if response is text, record it as goal detail"
        """TODO: to prevent emorec response being recorded, branch order
        in operate function is adjusted. It is error-prone."""
        context = message["context"]
        if message["type"] == 'text':
            key = self.key_list_goal_achievement % self.serialize_context(context)
            recent_response = json.loads(self.db.lpop(key))
            recent_response[1] = message["data"]["text"]
            self.db.lpush(key, json.dumps(recent_response))
            self.send_text(context, sr.RESPONSE_RECORDED)
            logging.debug('recent_response: %r', recent_response)
        self.user.state(context, '')

    def record_goal_response(self, message):
        "record daily goal achievement and share it"
        context = message["context"]
        key = self.key_list_goal_achievement % self.serialize_context(context)
        file_id = message["data"]["file_ids"][-1]
        self.db.lpush(key, json.dumps([file_id, '']))
        target_chat = self.session.target_chat(self.user.session(context))
        sharing_message = sr.GOAL_SHARING_MESSAGE % self.user.nick(context)
        self.send_text({"chat_id":target_chat}, sharing_message)
        self.send_image({"chat_id":target_chat}, file_id)
        self.send_text(context, sr.ASK_GOAL_ACHIEVEMENT_DETAIL)
        self.user.state(context, 'asked_goal_detail')

    def record_emorec_response(self, message):
        "record emorec response and share it"
        context = message["context"]
        key = self.key_list_emorec_response % self.serialize_context(context)
        text = message["data"]["text"]
        self.db.lpush(key, json.dumps([text, '']))
        reactive_sentence = emorec.REPLYS[emorec.EMOTIONS.index(text)]
        self.send_text(context, reactive_sentence + ' ' + sr.ASK_EMOTION_DETAIL)
        self.user.state(context, 'asked_emotion_detail')

        # sharing the response
        target_chat = self.session.target_chat(self.user.session(context))
        if target_chat is not None:
            sharing_message = sr.EMOREC_SHARING_MESSAGE % text
            self.send_text({"chat_id":target_chat}, sharing_message)

    def emorec_routine(self, message):
        "check if it has to ask emotions for some user"
        current = json.loads(message["data"]["time"])
        hour, minute = map(int, current[3:5])
        datetime_now = datetime.datetime(100, 1, 1, hour, minute, 0)
        for context in self.user.list_of_users():
            b_hour, b_minute = self.user.emorec_time(context)
            logging.debug('%r:%r', b_hour, b_minute)
            if b_hour == -1:
                continue
            datetime_baseline = datetime.datetime(100, 1, 1, b_hour, b_minute, 0)
            elapsed_seconds = (datetime_now - datetime_baseline).seconds
            if datetime_baseline < datetime_now and elapsed_seconds <= 600:
                if not self.user.emorec_block(context):
                    logging.debug('not blocked')
                    self.send({
                        "type": 'markup_text',
                        "context": context,
                        "data": {
                            "text": sr.ASK_EMOTION,
                            "reply_markup": emorec.KEYBOARD,
                            }
                        })
                    self.user.emorec_time(context, True)
                    self.user.emorec_block(context, True)


    def operator(self, message):
        context = message["context"]
        if context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN:
            if message["type"] == 'text':
                text = message["data"]["text"]
                if text == sr.COMMAND_PUBLISH_REGISTRATION_KEY:
                    self.send_text(context, self.user.generate_new_registration_key())
                elif text.split()[0] == sr.COMMAND_MAKE_SESSION:
                    session_name = self.session.create(
                        list(map(self.parse_context, text.split()[1:-1])))
                    self.session.target_chat(session_name, text.split()[-1])
                    self.send_text(context, 'created session: %s, target chat is %s' %
                                   (session_name, text.split()[-1]))
        elif self.user.membership_test(context):
            state = self.user.state(context)
            if emorec.is_emorec_response(message):
                self.record_emorec_response(message)
            elif message["type"] == 'image':
                self.record_goal_response(message)
            elif state is not None:
                getattr(self, 'state_' + state)(message)
            else:
                self.send_text(context, 'meow')

        elif message["type"] == 'text' and self.user.is_registration_key(message["data"]["text"]):
            self.user.register_user(context, message["data"]["text"])
            self.send_text(context, sr.REGISTER_COMPLETE)
            self.send_text(context, sr.ASK_NICKNAME)
            self.user.state(context, 'asked_nick')
        elif message["type"] == 'timer':
            self.emorec_routine(message)

        else:
            logging.error('This clause should never be executed!')
