import threading
import logging
import json
import time
import requests
import bot_config

from database_wrapper_redis import DatabaseWrapperRedis

class InterfaceTelegramSender(threading.Thread):
    def __init__(self):
        super().__init__()
        self.db = DatabaseWrapperRedis(host=bot_config.db_host, port=bot_config.db_port, db=bot_config.db_num)
        self.pubsub = self.db.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('channel-from-module-to-sender')
        self.__exit = False

    def run(self):
        while not self.__exit:
            message = self.pubsub.get_message()
            if message is not None:
                message = json.loads(message["data"].decode('utf-8'))
                self.send_message(message["chat_id"], message["text"])
            time.sleep(1)

    def shutdown(self):
        self.__exit = True

    def send_message(self, cid, text):
        t = threading.Thread(target = requests.post,
            args = (bot_config.api_base + 'sendMessage', ),
            kwargs = {
                'data': {
                    "chat_id" : cid,
                    "text" : text
                    }
                }
            )
        t.setDaemon(True)
        t.start()
