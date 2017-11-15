"""
Module for peer-motivational habit formation
This module contains
    - registration routine
    - goal achievement & sharing
    - team notification
"""

import logging
import random
import json


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
            self.session_routine(message)
        else:
            logging.error('This clause should never be executed!')

    def session_routine(self, message):
        "manages sessions at 9 and 22 o' clock"
        current_time = json.loads(message["data"]["time"])
        year, _month, _day, hour, _minute, _second, _wday, yday = current_time[:8]
        absolute_day = (year-2000) * 400 + yday
        hour = 10
        for context in self.user.list_of_users():
            if hour >= 9 and self.user.last_morning_routine(context) < absolute_day:
                self.user.last_morning_routine(context, absolute_day)
                self.morning_routine(context, absolute_day)
            elif hour >= 22 and self.user.last_reminder_routine(context) < absolute_day:
                self.user.last_reminder_routine(context, absolute_day)
                self.reminder_routine(context, absolute_day)

    def morning_routine(self, context, absolute_day):
        pass

    def reminder_routine(self, context, absolute_day):
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
        context = message["context"]
        try:
            if message["type"] == 'text' and \
               message["data"]["text"].startswith(sr.ADMIN_COMMAND_PREFIX):
                text = message["data"]["text"]
                text = text[len(sr.ADMIN_COMMAND_PREFIX):]
                args = text.split()
                if args[0] == sr.ADMIN_COMMAND_NOTICE:
                    content = text[len(args[0]):].strip()
                    cnt = 0
                    for target_context in self.user.list_of_users():
                        self.send_text(target_context, content)
                        cnt += 1
                    self.send_text(context, sr.REPORT_NOTICE_COMPLETE % cnt)
                elif args[0] == sr.ADMIN_COMMAND_LIST_USERS:
                    user_profiles = []
                    for target_context in self.user.list_of_users():
                        user_profiles.append(self.user.brief_info(target_context))
                    user_profiles = ['[%s] %s' % (i, j) for i, j in enumerate(user_profiles)]
                    for i in range(0, len(user_profiles), 10):
                        self.send_text(context, '\n'.join(user_profiles[i:i+10]))
                elif args[0] == sr.ADMIN_COMMAND_MAKE_PAIR:
                    ctx1, ctx2 = map(self.parse_context, args[1:3])
                    condition = args[3].upper()
                    if not (self.user.membership_test(ctx1) and self.user.membership_test(ctx2)):
                        self.send_text(context, sr.INVALID_CONTEXT)
                        return
                    if condition not in ['CONTROL', 'PSEUDO', 'REAL']:
                        self.send_text(context, sr.INVALID_CONDITION)
                        return
                    self.user.partner(ctx1, ctx2)
                    self.user.partner(ctx2, ctx1)
                    self.user.condition(ctx1, condition)
                    self.user.condition(ctx2, condition)
                    self.send_text(ctx1, getattr(sr, 'START_INSTRUCTION_%s' % condition))
                    self.send_text(ctx2, getattr(sr, 'START_INSTRUCTION_%s' % condition))
        except Exception as err: # pylint: disable=broad-except
            self.send_text(context, 'Error: %r' % err)

        """
        if message["type"] == 'callback_query':
            self.answer_callback_query(
                message["data"]["callback_query_id"],
                '응답이 기록되었습니다. 잘못 누르신 경우 1분 내에 다시 눌러주세요.')
        self.send({
            "type": "markup_text",
            "context": {"chat_id": bot_config.ADMIN},
            "data": {
                "text": '좋은 아침이에요! 오늘도 힘내서 일일 목표 달성해주세요!\n\n푸시업 45개, 레그레이즈 45개\n\n언제든 달성하고 나면 아래의 버튼을 눌러주세요.',
                "reply_markup": json.dumps({"inline_keyboard": [[
                    {"text": '0%', "callback_data": '1234567890123456789012345678901234567890123456789012345678901234'},
                    {"text": '25%', "callback_data": '25'},
                    {"text": '50%', "callback_data": '50'},
                    {"text": '75%', "callback_data": '75'},
                    {"text": '100%', "callback_data": '100'},
                ]]})
                }
            })

        self.send({
            "type": "markup_text",
            "context": {"chat_id": bot_config.ADMIN},
            "data": {
                "text": '파트너인 키 큰 형광 코끼리님에게서 오늘의 응답이 도착했어요!\n\n70%\n\n키 큰 형광 코끼리님을 위한 피드백을 보내주세요.',
                "reply_markup": json.dumps({"inline_keyboard": [
                    [{"text": '최고예요', "callback_data": '0'}],
                    [{"text": '멋져요', "callback_data": '25'}],
                    [{"text": '잘 하고 있어요', "callback_data": '50'}],
                    [{"text": '힘내세요', "callback_data": '75'}],
                    [{"text": '포기하지 말아요', "callback_data": '100'}],
                ]})
                }
            })
            """

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
