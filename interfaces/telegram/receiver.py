"""
Interface to receive messages from Telegram
"""

import threading
import logging
import json

import requests
import bot_config

from basic.database_wrapper_redis import DatabaseWrapperRedis

from flask import Flask, request


class InterfaceTelegramReceiver(threading.Thread):
    "This class is for receiveing messages from telegram by operating a Flask server"
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.db = DatabaseWrapperRedis(host=bot_config.DB_HOST, #pylint: disable=invalid-name
                                       port=bot_config.DB_PORT, db=bot_config.DB_NUM)

        self.app = Flask(__name__)
        @self.app.route("/", methods=['GET', 'POST'])
        def webhook(): #pylint: disable=unused-variable
            "listens to messages from Telegram webhook"
            try:
                data = request.get_json()
                if "message" in data or "callback_query" in data:
                    if "message" in data:
                        message = data["message"]
                        m_from = message["from"]
                    elif "callback_query" in data:
                        callback_query = data["callback_query"]
                        message = callback_query["message"]
                        m_from = callback_query["from"]
                    m_message = {}
                    # Parse Context
                    m_context = {
                        "chat_id": message["chat"]["id"],
                        "author_id": m_from["id"],
                        "author_name": m_from["first_name"],
                    }
                    if "last_name" in m_from:
                        m_context["author_name"] += ' ' + m_from["last_name"]
                    m_message["context"] = m_context

                    # Parse Data
                    m_data = {}
                    if 'photo' in message:
                        m_message["type"] = 'image'
                        m_data["text"] = 'PHOTO:%s' % message['photo'][-1]['file_id']
                        m_data["file_ids"] = [f['file_id'] for f in message['photo']]
                        if 'caption' in message:
                            m_data["caption"] = message['caption']
                    elif 'document' in message:
                        m_message["type"] = 'document'
                        m_data["file_id"] = message["document"]["file_id"]
                        m_data["text"] = 'DOCUMENT:%s' % m_data["file_id"]
                    else:
                        if "message" in data:
                            m_message["type"] = 'text'
                            m_data["text"] = message["text"]
                        elif "callback_query" in data:
                            m_message["type"] = 'callback_query'
                            m_data["text"] = callback_query["data"]

                    m_message["data"] = m_data
                    logging.info('RECV: %r', m_message)
                    if bot_config.DEBUG:
                        self.db.publish('debug-channel-from-interface-to-module',
                                        json.dumps(m_message))
                    else:
                        self.db.publish('channel-from-interface-to-module', json.dumps(m_message))

            except Exception as exception: #pylint: disable=broad-except
                logging.error('Error occured at webhook: %s', str(exception))
                logging.error('While handling the following data: %r', data)
            return ''

        @self.app.route("/shutdown", methods=['GET', 'POST'])
        def shutdown(): #pylint: disable=unused-variable
            "shutdown the Flask server"
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
            return ''

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=False)
    def shutdown(self):
        "sends http request to Flask server to call '/shutdown' inside"
        logging.debug('shutdown()')
        requests.get('http://%s:%s/shutdown' % (self.host, self.port))
