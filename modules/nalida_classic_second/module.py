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
        self.user = User(self)
        self.session = Session(self)
        self.key = {
            "list_goal_achievement": 'key-list-goal-achievement:%s',
            "list_emorec_response": 'key-emorec-response:%s',
            "temp_goal_response": 'key-temp-goal-response:%s',
            }

    def send_text(self, context, text):
        for subtext in text.split('$$$'):
            super().send_text(context, subtext)

    def send_to_monitoring(self, text):
        "send the text to monitoring room"
        self.send_text({"chat_id": bot_config.NALIDA_CLASSIC_SECOND_MONITORING}, text)

    def filter(self, message):
        context = message["context"]
        return any((
            context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN,
            message["type"] == 'text' and \
                message["data"]["text"].startswith(sr.COMMAND_PREFIX_REGISTER_BROADCASTING_ROOM),
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
                self.send_to_monitoring(sr.REPORT_NICKNAME % (serialized, nickname))
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
            nickname = self.user.nick(context)
            self.send_to_monitoring(sr.REPORT_EXPLANATION % (nickname, text))
            self.send_text(context, sr.EXPLANATION_SUBMITTED)
            self.send_text(context, sr.ASK_GOAL_NAME)
            self.user.state(context, 'asked_goal_name')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_goal_name(self, message):
        "response should be a name of the goal"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.user.goal_name(context, text)
            nickname = self.user.nick(context)
            self.send_to_monitoring(sr.REPORT_GOAL_NAME % (nickname, text))
            self.send_text(context, sr.GOAL_NAME_SUBMITTED)
            self.send_text(context, sr.ASK_GOAL_DESCRIPTION)
            self.user.state(context, 'asked_goal_description')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def state_asked_goal_description(self, message):
        "response should be the description of the goal in one message"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            self.user.goal_description(context, text)
            nickname = self.user.nick(context)
            self.send_to_monitoring(sr.REPORT_GOAL_DESCRIPTION % (nickname, text))
            self.send_text(context, sr.GOAL_DESCRIPTION_SUBMITTED)
            self.send_text(context, sr.INSTRUCTIONS_FOR_GOAL)
            self.send_text(context, sr.INSTRUCTIONS_FOR_EMOREC)
            self.user.emorec_time(context, True)
            self.user.state(context, '')
        else:
            self.send_text(context, sr.WRONG_RESPONSE_FORMAT)

    def record_emorec_response(self, message):
        "record emorec response and share it"
        context = message["context"]
        key = self.key["list_emorec_response"] % self.serialize_context(context)
        text = message["data"]["text"]
        self.db.lpush(key, json.dumps([text, '']))
        reactive_sentence = emorec.REPLYS[emorec.EMOTIONS.index(text)]
        self.send_text(context, reactive_sentence + ' ' + sr.ASK_EMOTION_DETAIL)
        self.user.state(context, 'asked_emotion_detail')

        nickname = self.user.nick(context)
        self.send_to_monitoring(sr.REPORT_EMOREC_SHARING % (nickname, text))

        if self.user.session(context) is None:
            return
        message_to_share = {
            "type": 'text',
            "context": None,
            "data": {
                "text": sr.EMOREC_SHARING_MESSAGE % text,
                }
            }
        self.session.share_user_response(context, message_to_share)

    def state_asked_emotion_detail(self, message):
        "record emotion response detail"
        context = message["context"]
        if message["type"] == 'text':
            key = self.key["list_emorec_response"] % self.serialize_context(context)
            text = message["data"]["text"]
            share = True
            if text.startswith(sr.COMMAND_NOT_TO_SHARE_EMOTION):
                text = text[len(sr.COMMAND_NOT_TO_SHARE_EMOTION):].strip()
                share = False
            recent_response = json.loads(self.db.lpop(key))
            recent_response[1] = text
            self.db.lpush(key, json.dumps(recent_response))
            nickname = self.user.nick(context)
            self.send_to_monitoring(sr.REPORT_EMOREC_DETAIL % (nickname, text))
            if share and self.user.session(context) is not None:
                message_to_share = {
                    "type": 'text',
                    "context": None,
                    "data": {
                        "text": sr.EMOREC_SHARING_DETAILED_MESSAGE % text
                        }
                    }
                self.session.share_user_response(context, message_to_share)
                self.send_text(context, sr.EMOREC_RESPONSE_RECORDED_AND_SHARED)
            else:
                self.send_text(context, sr.EMOREC_RESPONSE_RECORDED_BUT_NOT_SHARED)

        self.user.state(context, '')

    def record_goal_response(self, message):
        "send confirmation message"
        context = message["context"]
        self.user.state(context, 'asked_goal_confirmation')
        self.db.set(self.key["temp_goal_response"] % self.serialize_context(context),
                    json.dumps(message))
        self.send_text(context, sr.ASK_GOAL_RESPONSE_CONFIRMATION)


    def state_asked_goal_confirmation(self, message):
        "record daily goal achievement and share it"
        context = message["context"]
        if message["data"]["text"] != sr.RESPONSE_GOAL_YES:
            self.send_text(context, sr.REQUEST_ANOTHER_PICTURE)
            self.user.state(context, '')
            return
        info = self.db.get(self.key["temp_goal_response"] % self.serialize_context(context))
        message = json.loads(info)

        key = self.key["list_goal_achievement"] % self.serialize_context(context)
        file_id = message["data"]["file_ids"][-1]
        self.db.lpush(key, json.dumps([file_id, '']))
        self.send_text(context, sr.ASK_GOAL_ACHIEVEMENT_DETAIL)
        self.user.state(context, 'asked_goal_detail')

        if self.user.session(context) is not None:
            message_to_share = {
                "type": 'text',
                "context": None,
                "data": {
                    "text": sr.GOAL_SHARING_MESSAGE %
                            (self.user.nick(context), self.user.goal_name(context))
                    }
                }
            self.session.share_user_response(context, message_to_share)
            message_to_share["context"] = {
                "chat_id": bot_config.NALIDA_CLASSIC_SECOND_MONITORING
                }
            self.send(message_to_share)

            message_to_share = {
                "type": 'image',
                "context": None,
                "data": {
                    "file_ids": [file_id],
                    }
                }
            self.session.share_user_response(context, message_to_share)
            message_to_share["context"] = {
                "chat_id": bot_config.NALIDA_CLASSIC_SECOND_MONITORING
                }
            self.send(message_to_share)

    def state_asked_goal_detail(self, message):
        "if response is text, record it as goal detail"
        context = message["context"]
        if message["type"] == 'text':
            text = message["data"]["text"]
            share = True
            if text.startswith(sr.COMMAND_NOT_TO_SHARE_GOAL):
                text = text[len(sr.COMMAND_NOT_TO_SHARE_GOAL):].strip()
                share = False
            key = self.key["list_goal_achievement"] % self.serialize_context(context)
            recent_response = json.loads(self.db.lpop(key))
            recent_response[1] = text
            self.db.lpush(key, json.dumps(recent_response))

            if share and self.user.session(context) is not None:
                message_to_share = {
                    "type": 'text',
                    "context": None,
                    "data": {
                        "text": sr.GOAL_SHARING_DETAILED_MESSAGE %
                                (self.user.nick(context), message["data"]["text"])
                        }
                    }
                self.session.share_user_response(context, message_to_share)
                self.send_text(context, sr.GOAL_RESPONSE_RECORDED_AND_SHARED)
                message_to_share["context"] = {
                    "chat_id": bot_config.NALIDA_CLASSIC_SECOND_MONITORING
                    }
                self.send(message_to_share)
            else:
                self.send_text(context, sr.GOAL_RESPONSE_RECORDED_BUT_NOT_SHARED)
        self.user.state(context, '')

    def emorec_routine(self, message):
        "check if it has to ask emotions for some user"
        current = json.loads(message["data"]["time"])
        hour, minute = map(int, current[3:5])
        datetime_now = datetime.datetime(100, 1, 1, hour, minute, 0)
        for context in self.user.list_of_users():
            b_hour, b_minute = self.user.emorec_time(context)
            if b_hour == -1:
                continue
            datetime_baseline = datetime.datetime(100, 1, 1, b_hour, b_minute, 0)
            if datetime_baseline <= datetime_now:
                self.send({
                    "type": 'markup_text',
                    "context": context,
                    "data": {
                        "text": sr.ASK_EMOTION,
                        "reply_markup": emorec.KEYBOARD,
                        }
                    })
                self.user.emorec_time(context, True)

    def execute_admin_command(self, message):
        "executes commands entered in the admin room"
        try:
            context = message["context"]
            if message["type"] == 'text':
                text = message["data"]["text"]
                args = text.split()
                if text == sr.COMMAND_PUBLISH_REGISTRATION_KEY:
                    self.send_text(context, self.user.generate_new_registration_key())
                elif args[0] == sr.COMMAND_MAKE_SESSION:
                    nicks = args[1:]
                    target_contexts = []
                    for nick in nicks:
                        for target_context in self.user.list_of_users():
                            if self.user.nick(target_context) == nick:
                                target_contexts.append(target_context)
                    if len(target_contexts) != len(nicks):
                        self.send_text(context, sr.ERROR_MAKE_SESSION_INVALID_CONTEXT)
                        return
                    if not all(map(self.user.membership_test, target_contexts)):
                        self.send_text(context, sr.ERROR_MAKE_SESSION_INVALID_CONTEXT)
                        return
                    for target_context in target_contexts:
                        if self.user.target_chat(target_context) is None:
                            self.send_text(context, sr.ERROR_MAKE_SESSION_NO_TARGET_CHAT %
                                           self.user.nick(target_context))
                            return
                    session_name = self.session.create(target_contexts)
                    self.send_text(context, 'created session: %s' % session_name)
                elif args[0] == sr.COMMAND_NOTICE:
                    ind = text.find(':')
                    nicks = text[:ind].split()[1:]
                    content = text[ind+1:].strip()
                    target_contexts = []
                    for nick in nicks:
                        for target_context in self.user.list_of_users():
                            if self.user.nick(target_context) == nick:
                                target_contexts.append(target_context)
                                break
                    if len(nicks) != len(target_contexts):
                        self.send_text(context, sr.ERROR_NOTICE_INVALID_CONTEXT)
                        return
                    for target_context in target_contexts:
                        self.send_text(target_context, content)
                    self.send_text(context, sr.REPORT_NOTICE_COMPLETE)

        except Exception as exception: #pylint: disable=broad-except
            self.send_text({"chat_id": bot_config.NALIDA_CLASSIC_SECOND_ADMIN},
                           '에러가 발생했습니다: %s' % str(exception))

    def execute_user_command(self, message):
        "executes commands entered in user's chat"
        context = message["context"]
        state = self.user.state(context)
        if self.user.goal_description(context) is not None and \
                emorec.is_emorec_response(message):
            self.record_emorec_response(message)
        elif self.user.goal_description(context) is not None and message["type"] == 'image':
            self.record_goal_response(message)
        elif state is not None:
            getattr(self, 'state_' + state)(message)
        else:
            self.send_text(context, random.choice(sr.CAT_MEOWS))

    def operator(self, message):
        context = message["context"]
        if context["chat_id"] == bot_config.NALIDA_CLASSIC_SECOND_ADMIN:
            self.execute_admin_command(message)
        elif message["type"] == 'text' and \
                message["data"]["text"].startswith(sr.COMMAND_PREFIX_REGISTER_BROADCASTING_ROOM):
            text = message["data"]["text"]
            comm = sr.COMMAND_PREFIX_REGISTER_BROADCASTING_ROOM
            text = text[len(comm):].strip()
            context = self.parse_context(text)
            self.user.target_chat(context, self.serialize_context(message["context"]))
            self.send_text(message["context"],
                           sr.REGISTERED_AS_BROADCASTING_ROOM % self.user.nick(context))

        elif self.user.membership_test(context):
            self.execute_user_command(message)

        elif message["type"] == 'text' and self.user.is_registration_key(message["data"]["text"]):
            self.user.register_user(context, message["data"]["text"])
            self.send_text(context, sr.REGISTER_COMPLETE)
            self.send_text(context, sr.ASK_NICKNAME)
            self.user.state(context, 'asked_nick')
        elif message["type"] == 'timer':
            self.emorec_routine(message)

        else:
            logging.error('This clause should never be executed!')
