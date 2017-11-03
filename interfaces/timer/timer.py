"""
Timer module which will signal the elapse of time

Caution: this module does not guarantee that the signal is emitted every second,
         because signals are still unreliable as the program can stop functions
         for time to time.
         Client of the timer should be aware of and cope well with this unstableness.
"""
import threading
import time
import json

import bot_config
from basic.database_wrapper_redis import DatabaseWrapperRedis

class Timer(threading.Thread):
    "signals time object for every two seconds"
    def __init__(self):
        super().__init__()
        self.__exit = False
        self.database = DatabaseWrapperRedis(
            host=bot_config.DB_HOST, port=bot_config.DB_PORT,
            db=bot_config.DB_NUM, namespace=__name__)

    def run(self):
        while not self.__exit:
            message = {
                "type": "timer",
                "context": {"chat_id": -1, "author_id": -1},
                "data": {"time": json.dumps(time.localtime())}
                }
            self.database.publish('channel-from-interface-to-module', json.dumps(message))
            time.sleep(2)

    def shutdown(self):
        "shutdown the module"
        self.__exit = True
