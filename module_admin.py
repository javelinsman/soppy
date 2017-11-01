"""admin functions"""

import bot_config
from module import Module
from database_wrapper_redis import DatabaseWrapperRedis

class ModuleAdmin(Module):
    "implements several admin functions"
    def __init__(self):
        super().__init__(__name__)
        self.list_of_commands = [
            'greetings'
            ]
        self.database = DatabaseWrapperRedis(
            host=bot_config.DB_HOST, port=bot_config.DB_PORT,
            db=bot_config.DB_NUM)

    def filter(self, message):
        return message["context"]["chat_id"] == bot_config.GENERAL_ADMIN and \
               message["type"] == 'text' and \
               message["data"]["text"] in self.list_of_commands

    def operator(self, message):
        text = message["data"]["text"]
        if text == 'greetings':
            self.send_text(message["context"], 'Hello, Master!')
