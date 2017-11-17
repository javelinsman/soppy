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
import time


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
        self.key = {
            "last_morning_routine": 'last-morning-routine',
            "last_reminder_routine": 'last-reminder-routine'
            }

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
        if message["type"] != 'timer':
            self.db.rpush('real-log', json.dumps([time.time(), message]))
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

    @staticmethod
    def convert_to_int_default_zero(value):
        "convert value into int(convert) if it's not None, 0 o.w."
        return 0 if value is None else int(value)

    def session_routine(self, message):
        "manages sessions at 9 and 22 o' clock and handles bots"
        current_time = json.loads(message["data"]["time"])
        year, _month, _day, hour, _minute, second, _wday, yday = current_time[:8]
        if second % 60 not in [0, 1]:
            return
        absolute_day = (year-2000) * 400 + yday

        last_morning_routine = self.convert_to_int_default_zero(
            self.db.get(self.key["last_morning_routine"]))
        last_reminder_routine = self.convert_to_int_default_zero(
            self.db.get(self.key["last_reminder_routine"]))

        # Execute Morning Routine at Every 9 a.m.
        if hour >= 9 and last_morning_routine < absolute_day:
            self.db.set(self.key["last_morning_routine"], absolute_day)
            # Calculate Combo First
            for context in self.user.list_of_users():
                if self.user.condition(context) is not None:
                    if self.user.zero_day(context) != absolute_day: #ZERODAY
                        self.calculate_combo(context, absolute_day)
            for bot_pk in self.robot.list_of_robots():
                if self.robot.partner(bot_pk) is not None:
                    if self.robot.zero_day(bot_pk) != absolute_day: #ZERODAY
                        self.calculate_combo(bot_pk, absolute_day, True)
            # Execute morning routine for each user
            for context in self.user.list_of_users():
                if self.user.condition(context) is not None:
                    self.morning_routine(context, absolute_day)

        # Execute Reminder Routine at Every 10 p.m.
        if hour >= 22 and last_reminder_routine < absolute_day:
            self.db.set(self.key["last_reminder_routine"], absolute_day)
            reminder_sent_count = 0
            for context in self.user.list_of_users():
                if self.user.condition(context) is not None:
                    reminder_sent_count += self.reminder_routine(context, absolute_day)
            self.report('reminder sent to %d users' % reminder_sent_count)

        # Try bot's responses and feedbacks
        probability_parameter = 0.025
        for bot_pk in self.robot.list_of_robots():
            if self.robot.partner(bot_pk) is not None:
                # First Response Try
                if hour >= 9 and self.robot.last_first_try(bot_pk) < absolute_day:
                    if random.random() < probability_parameter:
                        self.robot.last_first_try(bot_pk, absolute_day)
                        self.robot_response_try(bot_pk, absolute_day)
                # Second Response Try if First One is Already Made
                elif hour >= 22 and self.robot.last_second_try(bot_pk) < absolute_day:
                    if random.random() < probability_parameter:
                        self.robot.last_second_try(bot_pk, absolute_day)
                        self.robot_response_try(bot_pk, absolute_day)
                # Feedback Try
                if self.robot.zero_day(bot_pk) != absolute_day: # ZERODAY
                    if hour >= 9 and self.robot.last_feedback_try(bot_pk) < absolute_day:
                        if random.random() < 0.025:
                            self.robot.last_feedback_try(bot_pk, absolute_day)
                            self.robot_feedback_try(bot_pk, absolute_day)

    def robot_response_try(self, bot_pk, absolute_day):
        "robot tries one challenge"
        prob = self.robot.prob(bot_pk)
        mean = self.robot.mean(bot_pk)
        sigma = self.robot.sigma(bot_pk)
        score = self.robot.score(bot_pk, absolute_day)
        if random.random() < prob:
            added = random.normalvariate(mean, sigma)
            new_score = min(score+added, 100)
            if int(score/25) != int(new_score/25):
                value = int(new_score/25)*25
                self.record_and_share_response_bot(bot_pk, value, absolute_day)
            self.robot.score(bot_pk, absolute_day, new_score)

    def robot_feedback_try(self, bot_pk, absolute_day):
        "robot tries feedback"
        prob = self.robot.prob(bot_pk)
        partner = self.robot.partner(bot_pk)
        if random.random() < prob:
            yesterday_response = self.user.response(partner, absolute_day-1)
            value = self.robot.evaluate_feedback(yesterday_response)
            self.record_and_share_feedback_bot(bot_pk, value, absolute_day-1)

    def calculate_combo(self, context, absolute_day, bot=False):
        "calculate combo"
        if bot:
            combo = self.robot.combo(context)
            yesterday_response = self.robot.response(context, absolute_day-1)
            def set_combo(value):
                "setter for robot"
                self.robot.combo(context, value)
        else:
            combo = self.user.combo(context)
            yesterday_response = self.user.response(context, absolute_day-1)
            def set_combo(value):
                "setter for human"
                self.user.combo(context, value)
        if yesterday_response in [75, 100]:
            set_combo(max(combo+1, 1))
        elif yesterday_response in [None, 0]:
            set_combo(min(combo-1, -1))
        else:
            set_combo(0)

    def morning_routine(self, context, absolute_day):
        "at 9 o'clock, gives summary and feedback, today's achievement message"
        condition = self.user.condition(context)
        serialized = self.serialize_context(context)

        if self.user.zero_day(context) != absolute_day: # ZERODAY

            # [1] My Summary of Yesterday
            self.send_text(context, self.user.summary(context, absolute_day-1))

            # [2] Partner's Summary if PESUDO or REAL
            if condition == 'PSEUDO':
                bot_pk = self.user.robot(context)
                self.send_text(context, self.robot.summary(bot_pk, absolute_day-1))
            elif condition == 'REAL':
                partner = self.user.partner(context)
                self.send_text(context, self.user.summary(partner, absolute_day-1))

            # [3] Automatically Evaluated Feedback if CONTROL
            #     Feedback Window if PSEUDO or REAL
            if condition == 'CONTROL':
                yesterday_response = self.user.response(context, absolute_day-1)
                ind = self.robot.evaluate_feedback(yesterday_response)
                self.send_text(context, sr.FEEDBACK_EVALUATED % sr.FEEDBACKS[ind])
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

        # [4] Today's Response Window
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
        if self.user.last_response_day(context) < absolute_day or \
           self.user.response(context, absolute_day) == 0:
            self.send_text(context, sr.REMINDER_FOR_RESPONSE)
            return 1
        return 0


    def record_and_share_response(self, context, value, absolute_day):
        "record context's reponse and share it if partner exists"
        self.user.response(context, absolute_day, value)
        self.user.last_response_day(context, absolute_day)
        if time.localtime().tm_hour < 9:
            return
        if self.user.condition(context) == 'REAL':
            partner = self.user.partner(context)
            self.send_text(partner, sr.RESPONSE_ARRIVED % (
                self.user.nick(context), value))

    def record_and_share_feedback(self, context, value, absolute_day):
        "record context's feedback to partner if it exists"
        if self.user.feedback(context, absolute_day) is None:
            self.user.feedback(context, absolute_day, value)
            if time.localtime().tm_hour < 9:
                return
            if self.user.condition(context) == 'REAL':
                partner = self.user.partner(context)
                self.send_text(partner, sr.FEEDBACK_ARRIVED % (
                    self.user.nick(context), sr.FEEDBACKS[value]))
            return True
        return False

    def record_and_share_response_bot(self, bot_pk, value, absolute_day):
        "for bot"
        self.robot.response(bot_pk, absolute_day, value)
        if time.localtime().tm_hour < 9:
            return
        partner = self.robot.partner(bot_pk)
        self.send_text(partner, sr.RESPONSE_ARRIVED % (
            self.robot.nick(bot_pk), value))

    def record_and_share_feedback_bot(self, bot_pk, value, absolute_day):
        "for bot"
        self.robot.feedback(bot_pk, absolute_day, value)
        if time.localtime().tm_hour < 9:
            return
        partner = self.robot.partner(bot_pk)
        self.send_text(partner, sr.FEEDBACK_ARRIVED % (
            self.robot.nick(bot_pk), sr.FEEDBACKS[value]))


    def execute_user_command(self, message):
        "executes commands entered in user's chat"
        context = message["context"]
        state = self.user.state(context)
        current_time = time.localtime()
        year = current_time.tm_year
        yday = current_time.tm_yday
        hour = current_time.tm_hour
        absolute_today = (year-2000) * 400 + yday
        if state is not None:
            getattr(self, 'state_' + state)(message)
        elif message["type"] == 'callback_query':
            def answer(text=''):
                "answer the callback query with text"
                self.answer_callback_query(message["data"]["callback_query_id"], text)
            callback_type, absolute_day, _serialized, value = message["data"]["text"].split(';')
            absolute_day, value = map(int, (absolute_day, value))
            if callback_type == 'feedback':
                answer()
                if absolute_day < absolute_today - 2 or \
                   (absolute_day == absolute_today - 2 and hour >= 9):
                    self.send_text(context, sr.INVALID_TOO_OLD)
                    return
                prev_feedback = self.user.feedback(context, absolute_day)
                if prev_feedback is None or prev_feedback != value:
                    if self.record_and_share_feedback(context, value, absolute_day):
                        self.send_text(context,
                                       sr.FEEDBACK_RECORDED_AND_SHARED % sr.FEEDBACKS[value])
                    else:
                        self.send_text(context, sr.FEEDBACK_ALREADY_RECORDED)
            elif callback_type == 'response':
                answer()
                if absolute_day < absolute_today - 1 or \
                   (absolute_day == absolute_today - 1 and hour >= 9):
                    self.send_text(context, sr.INVALID_TOO_OLD)
                    return
                prev_response = self.user.response(context, absolute_day)
                if prev_response is None or prev_response != value:
                    self.record_and_share_response(context, value, absolute_day)
                    if self.user.condition(context) == 'CONTROL':
                        self.send_text(context, sr.RESPONSE_RECORDED % value)
                    else:
                        self.send_text(context, sr.RESPONSE_RECORDED_AND_SHARED % value)
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
                elif args[0] == sr.ADMIN_COMMAND_CONDITIONAL_NOTICE:
                    condition = args[1]
                    content = text[len(text.split(':')[0])+1:].strip()
                    cnt = 0
                    for target_context in self.user.list_of_users():
                        if self.user.condition(target_context) is not None:
                            if self.user.condition(target_context) == condition:
                                self.send_text(target_context, content)
                                cnt += 1
                    self.send_text(context, sr.REPORT_NOTICE_COMPLETE % cnt)
                elif args[0] == sr.ADMIN_COMMAND_PRESENT_CONDITION:
                    absolute_day = int(args[1])
                    cnt = {"REAL": 0, "PSEUDO": 0, "CONTROL": 0}
                    prog = {"REAL": 0, "PSEUDO": 0, "CONTROL": 0}
                    cnt2 = {"REAL": 0, "PSEUDO": 0, "CONTROL": 0}
                    for target_context in self.user.list_of_users():
                        cond = self.user.condition(target_context)
                        if cond in cnt and \
                           self.user.response(target_context, absolute_day) is not None:
                            cnt[cond] += 1
                            prog[cond] += self.user.response(target_context, absolute_day)
                        if cond in cnt2:
                            cnt2[cond] += 1
                    self.send_text(context, 'CONTROL: %d/%d, PSEUDO: %d/%d, REAL: %d/%d' %
                                   (cnt["CONTROL"], cnt2["CONTROL"], cnt["PSEUDO"], cnt2["PSEUDO"],
                                    cnt["REAL"], cnt2["REAL"]))
                    self.send_text(context, 'CONTROL: %d, PSEUDO: %d, REAL: %d' %
                                   (prog["CONTROL"]/cnt2["CONTROL"], prog["PSEUDO"]/cnt2["PSEUDO"],
                                    prog["REAL"]/cnt2["REAL"]))
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
                    current_time = time.localtime()
                    year = current_time.tm_year
                    yday = current_time.tm_yday
                    absolute_day = (year-2000) * 400 + yday
                    if condition == 'CONTROL':
                        ctx = self.parse_context(args[2])
                        if self.user.membership_test(ctx):
                            self.user.condition(ctx, condition)
                            self.user.zero_day(ctx, absolute_day)
                            self.send_text(ctx, sr.START_INSTRUCTION_CONTROL)
                        else:
                            self.send_text(context, sr.INVALID_CONTEXT)
                    elif condition == 'PSEUDO':
                        ctx = self.parse_context(args[2])
                        bot_pk = args[3]
                        if self.user.membership_test(ctx) and self.robot.membership_test(bot_pk):
                            self.user.condition(ctx, condition)
                            self.user.zero_day(ctx, absolute_day)
                            self.user.robot(ctx, bot_pk)
                            self.robot.partner(bot_pk, ctx)
                            self.robot.zero_day(bot_pk, absolute_day)
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
                            self.user.zero_day(ctx1, absolute_day)
                            self.user.zero_day(ctx2, absolute_day)
                            self.send_text(ctx1, sr.START_INSTRUCTION_REAL)
                            self.send_text(ctx2, sr.START_INSTRUCTION_REAL)
                        else:
                            self.send_text(context, sr.INVALID_CONTEXT)
                    else:
                        self.send_text(context, sr.INVALID_CONDITION)

        except Exception as err: # pylint: disable=broad-except
            self.send_text(context, 'Error: %r' % err)

    def state_asked_goal_type(self, message):
        "state function"
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2', '3', '4']:
            return
        self.user.goal_type(context, message["data"]["text"])
        self.send_text(context, sr.ASK_GOAL_NAME)
        self.user.state(context, 'asked_goal_name')

    def state_asked_goal_name(self, message):
        "state function"
        context = message["context"]
        if message["type"] != 'text':
            return
        self.user.goal_name(context, message["data"]["text"])
        self.send_text(context, sr.ASK_DIFFICULTY % self.user.nick(context))
        self.user.state(context, 'asked_difficulty')

    def state_asked_difficulty(self, message):
        "state function"
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2', '3', '4', '5']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.difficulty(context, message["data"]["text"])
        self.send_text(context, sr.ASK_CONSCIENTIOUSNESS)
        self.user.state(context, 'asked_conscientiousness')

    def state_asked_conscientiousness(self, message):
        "state function"
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2', '3', '4']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.conscientiousness(context, message["data"]["text"])
        self.send_text(context, sr.ASK_AGE % self.user.nick(context))
        self.user.state(context, 'asked_age')

    def state_asked_age(self, message):
        "state function"
        context = message["context"]
        if message["type"] != 'text':
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.age(context, message["data"]["text"])
        self.send_text(context, sr.ASK_SEX % self.user.nick(context))
        self.user.state(context, 'asked_sex')

    def state_asked_sex(self, message):
        "state function"
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.sex(context, message["data"]["text"])
        self.send_text(context, sr.ASK_PUSH_ENABLE % self.user.nick(context))
        self.user.state(context, 'asked_push_enable')

    def state_asked_push_enable(self, message):
        "state function"
        context = message["context"]
        if message["type"] != 'text' or message["data"]["text"] not in ['1', '2']:
            self.send_text(context, sr.WRONG_RESPONSE)
            return
        self.user.push_enable(context, message["data"]["text"])
        self.report(self.user.brief_info(context))
        self.send_text(context, sr.REGISTRATION_COMPLETE)
        self.user.state(context, '')
