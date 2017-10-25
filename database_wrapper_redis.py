import redis

def byte_to_string(byte_string):
    return byte_string.decode('utf-8')

def convert_all_byte_to_string(obj):
    if type(obj) == bytes:
        return byte_to_string(obj)
    elif type(obj) in (list, tuple, set):
        return type(obj)(map(convert_all_byte_to_string, obj))
    elif type(obj) == dict:
        return dict(map(convert_all_byte_to_string, obj.items()))
    else:
        return obj

class DatabaseWrapperRedis:
    def __init__(self, host, port, db):
        self.db = redis.StrictRedis(host, port, db)
    def __getattr__(self, attr_name):
        def f(*args, **kwargs):
            return convert_all_byte_to_string(getattr(self.db, attr_name)(*args, **kwargs))
        return f
