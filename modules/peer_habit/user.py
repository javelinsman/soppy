"manages user informations for nalida classic 2nd"

import random
import string

from basic.module import Module

class User:
    "mainly about getters and setters"
    def __init__(self, parent):
        self.db = parent.db #pylint: disable=invalid-name
        self.key = {
            "state": 'user-state:%s',
            "nick": 'user-nick:%s',
            "goal_type": 'user-goal-type:%s',
            "goal_name": 'user-goal-name:%s',
            "difficulty": 'user-difficulty:%s',
            "conscientiousness": 'user-conscientiousness:%s',
            "age": 'user-age:%s',
            "sex": 'user-sex:%s',
            "push_enable": 'user-push-enable:%s',
            "registered_users": 'user-registered-users',
            "registration_keys": 'user-registration-keys',
            }

    def membership_test(self, context):
        "check if the context is registered for this module"
        return self.db.sismember(self.key["registered_users"], Module.serialize_context(context))

    def random_name(self):
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
        return list(map(Module.parse_context, users))

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

    def getset(self, varname, context, value=None):
        serialized = Module.serialize_context(context)
        state_key = self.key[varname] % serialized
        if value is None:
            result = self.db.get(state_key)
            return None if result == '' else result
        else:
            self.db.set(state_key, value)

    def state(self, *args, **kwargs):
        return self.getset('state', *args, **kwargs)

    def nick(self, *args, **kwargs):
        return self.getset('nick', *args, **kwargs)

    def goal_type(self, *args, **kwargs):
        return self.getset('goal_type', *args, **kwargs)

    def goal_name(self, *args, **kwargs):
        return self.getset('goal_name', *args, **kwargs)

    def difficulty(self, *args, **kwargs):
        return self.getset('difficulty', *args, **kwargs)

    def conscientiousness(self, *args, **kwargs):
        return self.getset('conscientiousness', *args, **kwargs)

    def age(self, *args, **kwargs):
        return self.getset('age', *args, **kwargs)

    def sex(self, *args, **kwargs):
        return self.getset('sex', *args, **kwargs)

    def push_enable(self, *args, **kwargs):
        return self.getset('push_enable', *args, **kwargs)

    def brief_info(self, context):
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
