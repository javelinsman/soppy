from basic.database_wrapper_redis import DatabaseWrapperRedis
import bot_config

DATABASE = DatabaseWrapperRedis(
    host=bot_config.DB_HOST, port=bot_config.DB_PORT,
    db=bot_config.DB_NUM)

DATABASE.flushdb()
