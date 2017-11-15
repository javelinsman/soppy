"manages robots"

import random
import string

from basic.module import Module

class Robot:
    "mainly about getters and setters"
    def __init__(self, parent):
        self.db = parent.db #pylint: disable=invalid-name
        self.key = {
            "registered_robots": 'robot-registered-robots',
            "primary_keys": 'robot-primary-keys'
            }

    @staticmethod
    def random_name():
        "generate random name"
        aaa = ['멋쟁이', '귀여운', '커다란', '키 큰', '사려깊은', '활발한', '지적인', '용맹한', '개구장이', '여유로운']
        bbb = ['붉은', '푸른', '보랏빛', '주황', '초록', '하늘색', '핑크', '노랑', '형광', '투명']
        ccc = ['조랑말', '들소', '맘모스', '코끼리', '판다곰', '독수리', '호랑이', '사자', '반달곰', '돌고래']
        return ' '.join([random.choice(aaa), random.choice(bbb), random.choice(ccc)])

    def create_robot(self):
        "create a new robot"
        bot_pk = self.new_pk()
        self.db.sadd(self.key["registered_robots"], bot_pk)
        self.nick(bot_pk, self.random_name())
        self.prob(bot_pk, random.random() * 0.4 + 0.5)
        self.mean(bot_pk, random.random() * 50 + 25)
        self.sigma(bot_pk, random.random() * 10 + 5)
        return bot_pk

    def list_of_robots(self):
        "returns the list of robots"
        robots = self.db.smembers(self.key["registered_robots"])
        return sorted(robots)

    def membership_test(self, bot_pk):
        "membership test"
        return self.db.sismember(self.key["primary_keys"], bot_pk)

    def new_pk(self):
        "make new key, insert to db, and return it"
        while True:
            new_key = 'robot:%s' % ''.join([random.choice(string.ascii_letters) for _ in range(25)])
            if not self.membership_test(new_key):
                break
        self.db.sadd(self.key["primary_keys"], new_key)
        return new_key

    def getset(self, varname, bot_pk, value=None, **kwargs):
        "getset function for simple key-value pair"
        state_key = 'robot-%s:%s' % (varname.replace('_', '-'), bot_pk)
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

    def nick(self, *args, **kwargs):
        "nickname"
        return self.getset('nick', *args, **kwargs)

    def prob(self, *args, **kwargs):
        "probability"
        return self.getset('prob', *args, **kwargs, wrap=float)

    def mean(self, *args, **kwargs):
        "mean of normal dist."
        return self.getset('mean', *args, **kwargs, wrap=float)

    def sigma(self, *args, **kwargs):
        "std dev of normal dist."
        return self.getset('sigma', *args, **kwargs, wrap=float)

    def response(self, bot_pk, absolute_day, value=None):
        "response of the robot"
        return self.getset('response_of_%d' % absolute_day, bot_pk, value)

    def feedback(self, bot_pk, absolute_day, value=None):
        "feedback of the robot"
        return self.getset('feedback_of_%d' % absolute_day, bot_pk, value)

    def partner(self, *args, **kwargs):
        "experimental partner"
        return self.getset('partner', *args, **kwargs,
                           wrap=Module.parse_context, wrap_set=Module.serialize_context)


    def brief_info(self, bot_pk):
        "brief information of the robot"
        return '; '.join([
            'ROBOT',
            'pk: %r' % bot_pk,
            'nick: %r' % self.nick(bot_pk),
            'prob: %r' % self.prob(bot_pk),
            'mean: %r' % self.mean(bot_pk),
            'sigma: %r' % self.sigma(bot_pk),
            ])

    def summary(self, bot_pk, absolute_day):
        "summary of achievment with insights"
        nick = self.nick(bot_pk)
        perf = self.response(bot_pk, absolute_day)
        return '%s님의 어제 성과는 %r에요.' % (nick, perf)
