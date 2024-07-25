from app.main.core.config import Config
import aioredis


class RedisManager():

    def __init__(self):
        self.aioredis = aioredis.from_url(Config.REDIS_HOST, encoding=Config.REDIS_CHARSET, decode_responses=True)

redis_manager = RedisManager()
