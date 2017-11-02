"""
Interface that sends message to telegram
"""
import threading
import logging
import json
import time
import queue
from collections import defaultdict

import requests
import bot_config

from basic.database_wrapper_redis import DatabaseWrapperRedis

class InterfaceTelegramSender(threading.Thread):
    "Interface to send message to Telegram messenger"
    def __init__(self):
        super().__init__()
        self.database = DatabaseWrapperRedis(
            host=bot_config.DB_HOST, port=bot_config.DB_PORT, db=bot_config.DB_NUM)
        self.pubsub = self.database.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('channel-from-module-to-sender')
        self.__exit = False
        self.message_queues = defaultdict(queue.Queue)

    def run(self):
        while not self.__exit:
            # Firstly, fetch all messages from channel
            while True:
                message = self.pubsub.get_message()
                if message is None:
                    break
                message = json.loads(message["data"].decode('utf-8'))
                self.message_queues[message["context"]["chat_id"]].put(message)
            # Secondly, send one message for each chat_id's
            for chat_id, message_queue in list(self.message_queues.items()):
                if not message_queue.empty():
                    message = message_queue.get()
                    if message["type"] == 'text':
                        self.send_message(chat_id, message["data"]["text"])
                    elif message["type"] == 'markup_text':
                        self.send_message_with_markup(chat_id, message["data"]["text"],
                                                      message["data"]["reply_markup"])
                    elif message["type"] == 'image':
                        self.send_image(chat_id, message["data"]["file_ids"][-1])
                    elif message["type"] == 'document':
                        self.send_document(chat_id, message["data"]["file_id"])

            time.sleep(1)

    def shutdown(self):
        "stop the thread when called"
        self.__exit = True

    def send_message(self, cid, text):
        t = threading.Thread(target = requests.post,
            args = (bot_config.API_BASE + 'sendMessage', ),
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
            args = (bot_config.API_BASE + 'sendMessage', ),
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
            args = (bot_config.API_BASE + 'sendPhoto', ),
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
            args = (bot_config.API_BASE + 'sendDocument', ),
            kwargs = {
                'data': {
                    "chat_id" : cid,
                    "document" : fid,
                    }
                }
            )
        t.setDaemon(True)
        t.start()
