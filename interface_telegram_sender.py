import threading
import logging
import json
import time
import queue
import requests
import bot_config

from collections import defaultdict

from database_wrapper_redis import DatabaseWrapperRedis

class InterfaceTelegramSender(threading.Thread):
    def __init__(self):
        super().__init__()
        self.db = DatabaseWrapperRedis(host=bot_config.db_host, port=bot_config.db_port, db=bot_config.db_num)
        self.pubsub = self.db.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('channel-from-module-to-sender')
        self.__exit = False
        self.q = defaultdict(lambda:queue.Queue())

    def run(self):
        while not self.__exit:
            # Firstly, fetch all messages from channel
            while True:
                message = self.pubsub.get_message()
                if message is None:
                    break
                message = json.loads(message["data"].decode('utf-8'))
                self.q[message["context"]["chat_id"]].put(message)
            # Secondly, send one message for each chat_id's
            for chat_id, q in list(self.q.items()):
                if not q.empty():
                    message = q.get()
                    if message["type"] == 'text':
                        self.send_message(chat_id, message["data"]["text"])
                    elif message["type"] == 'markup_text':
                        self.send_message_with_markup(chat_id, message["data"]["text"], message["data"]["reply_markup"])
                    elif message["type"] == 'image':
                        self.send_image(chat_id, message["data"]["file_ids"][-1])
                    elif message["type"] == 'document':
                        self.send_document(chat_id, message["data"]["file_id"])

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

    def send_message_with_markup(self, cid, text, markup):
        t = threading.Thread(target = requests.post,
            args = (bot_config.api_base + 'sendMessage', ),
            kwargs = {
                'data': {
                    "chat_id" : cid,
                    "text" : text,
                    "reply_markup" : markup,
                    }
                }
            )
        t.setDaemon(True)
        t.start()

    def send_image(self, cid, fid, caption=''):
        logging.debug('send_image(%r, %r, %r)', cid, fid, caption)
        t = threading.Thread(target = requests.post,
            args = (bot_config.api_base + 'sendPhoto', ),
            kwargs = {
                'data': {
                    "chat_id" : cid,
                    "photo" : fid,
                    "caption" : caption
                    }
                }
            )
        t.setDaemon(True)
        t.start()

    def send_document(self, cid, fid):
        logging.debug('send_document(%r, %r)', cid, fid)
        t = threading.Thread(target = requests.post,
            args = (bot_config.api_base + 'sendDocument', ),
            kwargs = {
                'data': {
                    "chat_id" : cid,
                    "document" : fid,
                    }
                }
            )
        t.setDaemon(True)
        t.start()
