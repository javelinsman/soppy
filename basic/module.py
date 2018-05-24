"""
This module defines class Module. Its function is described below.
"""
import sys
import time
import json
import threading
import logging

import requests
import bot_config

from basic.database_wrapper_redis import DatabaseWrapperRedis

class Module(threading.Thread):
    """This class defines the skeleton structure of Nalinyang-Twix MODULEs,
        which are independent reactive components to handle messages
        broadcasted by receiver interfaces."""

    def __init__(self, module_name):
        logging.debug('Module "%s" __init__()', module_name)
        super().__init__()
        self.module_name = module_name
        self.db = DatabaseWrapperRedis( #pylint: disable=invalid-name
            host=bot_config.DB_HOST, port=bot_config.DB_PORT,
            db=bot_config.DB_NUM, namespace=module_name
            )
        self.pubsub = self.db.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe('channel-from-interface-to-module-soppy')
        self.__exit = False

    def run(self):
        while not self.__exit:
            while True:
                message = self.pubsub.get_message()
                if message is None:
                    break
                message = json.loads(message["data"].decode('utf-8'))
                if self.filter(message):
                    self.operator(message)
            time.sleep(1)

    @staticmethod
    def serialize_context(context):
        "make context information serialized to string"
        return '%s:%s' % (
            context["chat_id"],
            context["author_id"]
        )

    @staticmethod
    def parse_context(serialized):
        "convert serialized context string to context"
        chat_id, author_id = map(int, serialized.split(':'))
        return {"chat_id": chat_id, "author_id": author_id}

    def send(self, message):
        "broadcast message to sender interfaces"
        self.db.publish('channel-from-module-to-sender-soppy', json.dumps(message))

    def report(self, message):
        "broadcast message to sender interfaces"
        message["data"]["text"] = '[%s] ' % message["context"]["author_name"] + message["data"]["text"]
        message["context"] = {"chat_id": bot_config.REPORT, "author_id": bot_config.REPORT}
        self.db.publish('channel-from-module-to-sender-soppy', json.dumps(message))


    def send_text(self, context, text, interface_name):
        "send plain text to context"
        message = {
            "type": 'text',
            "context": context,
            "data": {"text": text},
            "from": interface_name,
            }
        self.send(message)

    def send_image(self, context, file_id):
        "send image to context"
        message = {
            "type": 'image',
            "context": context,
            "data": {"file_ids":[file_id]}
            }
        self.send(message)

    @staticmethod
    def answer_callback_query(cbq_id, text=''):
        "answer callback query with alerting text"
        thr = threading.Thread(
            target=requests.post,
            args=(bot_config.API_BASE + 'answerCallbackQuery', ),
            kwargs={
                'data': {
                    "callback_query_id" : cbq_id,
                    "text" : text,
                    }
                }
            )
        thr.setDaemon(True)
        thr.start()

    def shutdown(self):
        "this thread will be terminated soon when called"
        self.__exit = True

    def filter(self, message):
        "filter method should return True for messages of interest"
        logging.debug('filter(%s)', message)
        logging.error('"filter" method of Module "%s" is not overridden', self.module_name)
        sys.exit(0)

    def operator(self, message):
        "operator method should provide proper handlings for messages of interest"
        logging.debug('operator(%s)', message)
        logging.error('"operator" method of Module "%s" is not overridden', self.module_name)
        sys.exit(0)
