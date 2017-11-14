"Session for Nalida Classic 2nd"
import random
import string

from basic.module import Module

class Session:
    "mainly for get-set, also for creating"
    def __init__(self, parent):
        self.db = parent.db
        self.user = parent.user
        self.send = parent.send
        self.key = {
            "session_names": 'session-session-names',
            "users": 'session-users:%s',
            }

    def create(self, contexts):
        "create a new session and return session name"
        while True:
            session_name = ''.join([random.choice(string.ascii_letters) for _ in range(25)])
            if not self.db.sismember(self.key["session_names"], session_name):
                break
        self.db.sadd(self.key["session_names"], session_name)

        key_users = self.key["users"] % session_name
        for context in contexts:
            serialized = Module.serialize_context(context)
            self.db.sadd(key_users, serialized)
            self.user.session(context, session_name)

        return session_name

    def list_of_users(self, session_name):
        "getter for users in the session"
        return list(map(Module.parse_context, self.db.smembers(self.key["users"] % session_name)))

    def share_user_response(self, context, message):
        "share message to context's team members"
        session_name = self.user.session(context)
        contexts = self.list_of_users(session_name)
        for target_context in contexts:
            target_chat = self.user.target_chat(target_context)
            message["context"] = {"chat_id": target_chat}
            self.send(message)
