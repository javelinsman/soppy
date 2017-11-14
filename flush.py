from basic.database_wrapper_redis import DatabaseWrapperRedis
import bot_config

if bot_config.DEBUG:
    DATABASE = DatabaseWrapperRedis(
        host=bot_config.DB_HOST, port=bot_config.DB_PORT,
        db=bot_config.DB_NUM)

    DATABASE.flushdb()
else:
    print('It is in production mode. Did you really mean to flush it?')
