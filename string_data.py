"""
Wrapper class for string data
"""
from database_wrapper_redis import DatabaseWrapperRedis
import bot_config

class StringData:
    """This class sees if requested string
    exists in DB and returns it if it does,
    else it returns the name of the attribute"""

    def __init__(self):
        self.database = DatabaseWrapperRedis(
            host=bot_config.DB_HOST, port=bot_config.DB_PORT,
            db=bot_config.DB_NUM, namespace='string_data')

    def get(self, attr_name):
        "getter function, default return value is attr_name itself"
        data = self.database.get(attr_name)
        return data if data is not None else attr_name

    def set(self, attr_name, value):
        "setter function"
        self.database.set(attr_name, value)
