"Session for Nalida Classic 2nd"
import random
import string

from basic.module import Module

class Session:
    "mainly for get-set, also for creating"
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.key_session_names = 'session-session-names'
        self.key_users = 'session-users:%s'
        self.key_target_chat = 'session-target-chat:%s'

    def create(self, contexts):
        "create a new session and return session name"
        while True:
            session_name = ''.join([random.choice(string.ascii_letters) for _ in range(25)])
            if not self.db.sismember(self.key_session_names, session_name):
                break
        self.db.sadd(self.key_session_names, session_name)

        key_users = self.key_users % session_name
        for context in contexts:
            serialized = Module.serialize_context(context)
            self.db.sadd(key_users, serialized)
            self.user.session(context, session_name)

        return session_name

    def users(self, session_name):
        "getter for users in the session"
        return self.db.smembers(self.key_users % session_name)

    def target_chat(self, session_name, value=None):
        "getset for target chat"
        key = self.key_target_chat % session_name
        if value is None:
            return self.db.get(key)
        else:
            self.db.set(key, value)
