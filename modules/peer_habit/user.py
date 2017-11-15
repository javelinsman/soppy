"manages user informations for nalida classic 2nd"

import random
import string

from basic.module import Module

class User:
    "mainly about getters and setters"
    def __init__(self, parent):
        self.db = parent.db #pylint: disable=invalid-name
        self.key = {
            "registered_users": 'user-registered-users',
            "registration_keys": 'user-registration-keys',
            }

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key["registered_users"], Module.serialize_context(context))

    def random_name(self):
        "generate random name"
        a = ['멋쟁이', '귀여운', '커다란', '키 큰', '사려깊은', '활발한', '지적인', '용맹한', '개구장이', '여유로운']
        b = ['붉은', '푸른', '보랏빛', '주황', '초록', '하늘색', '핑크', '노랑', '형광', '투명']
        c = ['조랑말', '들소', '맘모스', '코끼리', '판다곰', '독수리', '호랑이', '사자', '반달곰', '돌고래']
        return ' '.join([random.choice(a), random.choice(b), random.choice(c)])

    def register_user(self, context, registration_key):
        "register the context as a user of this module"
        self.db.sadd(self.key["registered_users"], Module.serialize_context(context))
        self.nick(context, self.random_name())

    def list_of_users(self):
        "returns the list of registrated users"
        users = self.db.smembers(self.key["registered_users"])
        return list(map(Module.parse_context, sorted(users)))

    def generate_new_registration_key(self):
        "make new key, insert to db, and return it"
        while True:
            new_key = '%s:%s' % (
                'Nalida-Classic-Second',
                ''.join([random.choice(string.ascii_letters) for _ in range(25)])
                )
            if not self.is_registration_key(new_key):
                break
        self.db.sadd(self.key["registration_keys"], new_key)
        return new_key

    def is_registration_key(self, key):
        "check if the key is the registration key"
        return key == '연구참가'

    def getset(self, varname, context, value=None, **kwargs):
        "getset function for simple key-value pair"
        serialized = Module.serialize_context(context)
        state_key = 'user-%s:%s' % (varname.replace('_', '-'), serialized)
        if value is None:
            result = self.db.get(state_key)
            if result is None or result == '':
                if 'default' in kwargs:
                    return kwargs["default"]
                return None
            else:
                if 'wrap' in kwargs:
                    return kwargs["wrap"](result)
                return result

        else:
            if 'wrap_set' in kwargs:
                self.db.set(state_key, kwargs["wrap_set"](value))
            else:
                self.db.set(state_key, value)

    def state(self, *args, **kwargs):
        "user state"
        return self.getset('state', *args, **kwargs)

    def nick(self, *args, **kwargs):
        "nickname"
        return self.getset('nick', *args, **kwargs)

    def goal_type(self, *args, **kwargs):
        "type of the goal: 1, 2, 3, or 4"
        return self.getset('goal_type', *args, **kwargs)

    def goal_name(self, *args, **kwargs):
        "name of the goal"
        return self.getset('goal_name', *args, **kwargs)

    def difficulty(self, *args, **kwargs):
        "subjective difficulty of the goal"
        return self.getset('difficulty', *args, **kwargs)

    def conscientiousness(self, *args, **kwargs):
        "subjective perceived conscientiousness of the user"
        return self.getset('conscientiousness', *args, **kwargs)

    def age(self, *args, **kwargs):
        "age of the user"
        return self.getset('age', *args, **kwargs)

    def sex(self, *args, **kwargs):
        "sex of the user"
        return self.getset('sex', *args, **kwargs)

    def push_enable(self, *args, **kwargs):
        "whether push notification is enabled or not"
        return self.getset('push_enable', *args, **kwargs)

    def condition(self, *args, **kwargs):
        "experimental condition"
        return self.getset('condition', *args, **kwargs)

    def partner(self, *args, **kwargs):
        "experimental partner"
        return self.getset('partner', *args, **kwargs,
                           wrap=Module.parse_context, wrap_set=Module.serialize_context)

    def last_morning_routine(self, *args, **kwargs):
        "the last day that morning routine was performed"
        return self.getset('last_morning_routine', *args, **kwargs, default=0, wrap=int)

    def last_reminder_routine(self, *args, **kwargs):
        "the last day that reminder routine was performed"
        return self.getset('last_reminder_routine', *args, **kwargs, default=0, wrap=int)

    def last_response_day(self, *args, **kwargs):
        "the last day that the user sent response"
        return self.getset('last_response_day', *args, **kwargs, default=0, wrap=int)

    def response(self, context, absolute_day, value=None):
        "response of the user"
        return self.getset('response_of_%d' % absolute_day, context, value)

    def feedback(self, context, absolute_day, value=None):
        "feedback of the user"
        return self.getset('feedback_of_%d' % absolute_day, context, value)

    def brief_info(self, context):
        "brief information of the user"
        return '; '.join([
            'context: %r' % Module.serialize_context(context),
            'nick: %r' % self.nick(context),
            'goal_type: %r' % self.goal_type(context),
            'goal_name: %r' % self.goal_name(context),
            'difficulty: %r' % self.difficulty(context),
            'conscientiousness: %r' % self.conscientiousness(context),
            'age: %r' % self.age(context),
            'sex: %r' % self.sex(context),
            'push_enable: %r' % self.push_enable(context),
            ])

    def summary(self, context, absolute_day):
        "summary of achievment with insights"
        return 'summary for %d of %s' % (absolute_day, Module.serialize_context(context))
