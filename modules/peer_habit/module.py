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
from modules.peer_habit.robot import Robot
from modules.peer_habit.session import Session
from basic.module import Module

import bot_config

class ModulePeerHabit(Module):
    "Module description above"
    def __init__(self):
        super().__init__(__name__)
        self.user = User(self)
        self.robot = Robot(self)
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
        absolute_day = 8028
        hour = 9
        for context in self.user.list_of_users():
            if self.user.condition(context) is not None:
                if hour >= 9 and self.user.last_morning_routine(context) < absolute_day:
                    self.user.last_morning_routine(context, absolute_day)
                    self.morning_routine(context, absolute_day)
                elif hour >= 22 and self.user.last_reminder_routine(context) < absolute_day:
                    self.user.last_reminder_routine(context, absolute_day)
                    self.reminder_routine(context, absolute_day)
        for bot_pk in self.robot.list_of_robots():
            if self.robot.partner(bot_pk) is not None:
                #TODO random time
                if hour >= 9 and self.robot.last_first_try(bot_pk) < absolute_day:
                    self.robot.last_first_try(bot_pk, absolute_day)
                    self.robot_response_try(bot_pk, absolute_day)
                elif hour >= 22 and self.robot.last_second_try(bot_pk) < absolute_day:
                    self.robot.last_second_try(bot_pk, absolute_day)
                    self.robot_response_try(bot_pk, absolute_day)
                if hour >= 9 and self.robot.last_feedback_try(bot_pk) < absolute_day:
                    self.robot.last_feedback_try(bot_pk, absolute_day)
                    self.robot_feedback_try(bot_pk, absolute_day)

    def robot_response_try(self, bot_pk, absolute_day):
        "robot tries one challenge"
        print("robot tries!")
        prob = self.robot.prob(bot_pk)
        mean = self.robot.mean(bot_pk)
        sigma = self.robot.sigma(bot_pk)
        score = self.robot.score(bot_pk, absolute_day)
        if random.random() < prob:
            print("GOGOGO")
            added = random.normalvariate(mean, sigma)
            new_score = min(score+added, 100)
            print("new score becomes", new_score)
            if int(score/25) != int(new_score/25):
                value = int(new_score/25)*25
                print("value", value)
                self.robot.response(bot_pk, absolute_day, value)
                partner = self.robot.partner(bot_pk)
                self.send_text(partner, '%s%%' % value)
            self.robot.score(bot_pk, absolute_day, new_score)
        else:
            print("NO")

    def robot_feedback_try(self, bot_pk, absolute_day):
        "robot tries feedback"
        prob = self.robot.prob(bot_pk)
        partner = self.robot.partner(bot_pk)
        print('feedback try')
        if random.random() < prob:
            print('yes!')
            yesterday_response = self.user.response(partner, absolute_day-1)
            if yesterday_response is not None:
                ind = self.robot.evaluate_feedback(yesterday_response)
                self.send_text(partner, '%s' % sr.FEEDBACKS[ind])

    def morning_routine(self, context, absolute_day):
        "at 9 o'clock, gives summary and feedback, today's achievement message"
        self.send_text(context, self.user.summary(context, absolute_day-1))
        condition = self.user.condition(context)
        serialized = self.serialize_context(context)

        if condition in ['PSEUDO', 'REAL']:
            if condition == 'PSEUDO':
                bot_pk = self.user.robot(context)
                self.send_text(context, self.robot.summary(bot_pk, absolute_day-1))
            elif condition == 'REAL':
                partner = self.user.partner(context)
                self.send_text(context, self.user.summary(partner, absolute_day-1))

        if condition == 'CONTROL':
            yesterday_response = self.user.response(context, absolute_day-1)
            if yesterday_response is not None:
                ind = self.robot.evaluate_feedback(yesterday_response)
                self.send_text(context, '%s' % sr.FEEDBACKS[ind])
        else:
            callback_base = 'feedback;%s;%s;' % (absolute_day-1, serialized) + '%d'
            if condition == 'PSEUDO':
                nick = self.robot.nick(self.user.robot(context))
            else:
                nick = self.user.nick(self.user.partner(context))
            self.send({
                "type": "markup_text",
                "context": context,
                "data": {
                    "text": sr.FEEDBACK_INTRO % nick,
                    "reply_markup": json.dumps({"inline_keyboard": [
                        [{"text": sr.FEEDBACKS[4], "callback_data": callback_base % 4}],
                        [{"text": sr.FEEDBACKS[3], "callback_data": callback_base % 3}],
                        [{"text": sr.FEEDBACKS[2], "callback_data": callback_base % 2}],
                        [{"text": sr.FEEDBACKS[1], "callback_data": callback_base % 1}],
                        [{"text": sr.FEEDBACKS[0], "callback_data": callback_base % 0}],
                    ]})
                    }
                })

        callback_base = 'response;%s;%s;' % (absolute_day, serialized) + '%d'
        self.send({
            "type": "markup_text",
            "context": context,
            "data": {
                "text": sr.RESPONSE_INTRO % self.user.goal_name(context),
                "reply_markup": json.dumps({"inline_keyboard": [[
                    {"text": '0%', "callback_data": callback_base % 0},
                    {"text": '25%', "callback_data": callback_base % 25},
                    {"text": '50%', "callback_data": callback_base % 50},
                    {"text": '75%', "callback_data": callback_base % 75},
                    {"text": '100%', "callback_data": callback_base % 100},
                ]]})
                }
            })

    def reminder_routine(self, context, absolute_day):
        "send reminder if the user hasn't sent any response yet"
        if self.user.last_response_day(context) < absolute_day:
            self.send_text(context, sr.REMINDER_FOR_RESPONSE)

    def record_and_share_response(self, context, value, absolute_day):
        "record context's reponse and share it if partner exists"
        self.user.response(context, absolute_day, value)
        self.user.last_response_day(context, absolute_day)
        if self.user.condition(context) == 'REAL':
            partner = self.user.partner(context)
            self.send_text(partner, '%s%%' % value)

    def record_and_share_feedback(self, context, value, absolute_day):
        "record context's feedback to partner if it exists"
        if self.user.feedback(context, absolute_day) is None:
            self.user.feedback(context, absolute_day, value)
            if self.user.condition(context) == 'REAL':
                partner = self.user.partner(context)
                self.send_text(partner, sr.FEEDBACKS[value])
            return True
        return False

    def execute_user_command(self, message):
        "executes commands entered in user's chat"
        context = message["context"]
        state = self.user.state(context)
        if state is not None:
            getattr(self, 'state_' + state)(message)
        elif message["type"] == 'callback_query':
            def answer(text=''):
                "answer the callback query with text"
                self.answer_callback_query(message["data"]["callback_query_id"], text)
            callback_type, absolute_day, _serialized, value = message["data"]["text"].split(';')
            absolute_day, value = map(int, (absolute_day, value))
            if callback_type == 'feedback':
                if self.record_and_share_feedback(context, value, absolute_day):
                    answer('피드백이 기록되고 공유되었습니다: %s' % sr.FEEDBACKS[value])
                else:
                    answer('이미 피드백을 기록하셨습니다.')
            elif callback_type == 'response':
                self.record_and_share_response(context, value, absolute_day)
                if self.user.condition(context) == 'CONTROL':
                    answer('응답이 기록되었습니다: %s%%' % value)
                else:
                    answer('응답이 기록되고 공유되었습니다: %s%%' % value)
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
                elif args[0] == sr.ADMIN_COMMAND_CREATE_ROBOT:
                    bot_pk = self.robot.create_robot()
                    self.send_text(context, self.robot.brief_info(bot_pk))
                elif args[0] == sr.ADMIN_COMMAND_LIST_USERS:
                    user_profiles = []
                    for target_context in self.user.list_of_users():
                        user_profiles.append(self.user.brief_info(target_context))
                    user_profiles = ['[%s] %s' % (i, j) for i, j in enumerate(user_profiles)]
                    for i in range(0, len(user_profiles), 10):
                        self.send_text(context, '\n'.join(user_profiles[i:i+10]))
                elif args[0] == sr.ADMIN_COMMAND_LIST_ROBOTS:
                    robot_profiles = []
                    for bot_pk in self.robot.list_of_robots():
                        robot_profiles.append(self.robot.brief_info(bot_pk))
                    robot_profiles = ['[R%s] %s' % (i, j) for i, j in enumerate(robot_profiles)]
                    for i in range(0, len(robot_profiles), 10):
                        self.send_text(context, '\n'.join(robot_profiles[i:i+10]))
                elif args[0] == sr.ADMIN_COMMAND_MAKE_PAIR:
                    condition = args[1].upper()
                    if condition == 'CONTROL':
                        ctx = self.parse_context(args[2])
                        if self.user.membership_test(ctx):
                            self.user.condition(ctx, condition)
                            self.send_text(ctx, sr.START_INSTRUCTION_CONTROL)
                        else:
                            self.send_text(context, sr.INVALID_CONTEXT)
                    elif condition == 'PSEUDO':
                        ctx = self.parse_context(args[2])
                        bot_pk = args[3]
                        if self.user.membership_test(ctx) and self.robot.membership_test(bot_pk):
                            self.user.condition(ctx, condition)
                            self.user.robot(ctx, bot_pk)
                            self.robot.partner(bot_pk, ctx)
                            self.send_text(ctx, sr.START_INSTRUCTION_PSEUDO)
                        else:
                            self.send_text(context, sr.INVALID_CONTEXT)
                    elif condition == 'REAL':
                        ctx1, ctx2 = map(self.parse_context, args[2:4])
                        if self.user.membership_test(ctx1) and self.user.membership_test(ctx2):
                            self.user.partner(ctx1, ctx2)
                            self.user.partner(ctx2, ctx1)
                            self.user.condition(ctx1, condition)
                            self.user.condition(ctx2, condition)
                            self.send_text(ctx1, sr.START_INSTRUCTION_REAL)
                            self.send_text(ctx2, sr.START_INSTRUCTION_REAL)
                        else:
                            self.send_text(context, sr.INVALID_CONTEXT)
                    else:
                        self.send_text(context, sr.INVALID_CONDITION)

        except Exception as err: # pylint: disable=broad-except
            self.send_text(context, 'Error: %r' % err)

        """
        if message["type"] == 'callback_query':
            self.answer_callback_query(
                message["data"]["callback_query_id"],
                '응답이 기록되었습니다. 잘못 누르신 경우 1분 내에 다시 눌러주세요.')

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
