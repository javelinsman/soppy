import threading
import logging

import requests

from flask import Flask, request

class InterfaceTelegram(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        @self.app.route("/", methods=['GET','POST'])
        def webhook():
            try:
                data = request.get_json()
                args = SimpleNamespace()
                args.type = ''
                if "message" in data:
                    message = data["message"]
                    args.chat_id = message["chat"]["id"]
                    args.author_id = message["from"]["id"]
                    args.author_name = message["from"]["first_name"]
                    args.text = message["text"]
                    args.type = 'text'
                    print(args.author_name, args.text)
            except Exception as e:
                print("Error: ", str(e))
                print(data)
            return ''
        @self.app.route("/shutdown", methods=['GET', 'POST'])
        def shutdown():
            func = request.environ.get('werkzeug.server.shutdown')
            if func is not None:
                func()
            return ''
    def run(self):
        self.app.run(host=self.host, port=self.port, debug=False)
    def shutdown(self):
        logging.debug('shutdown()')
        requests.get('http://%s:%s/shutdown' % (self.host, self.port))
