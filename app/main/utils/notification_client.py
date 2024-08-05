import redis
import json
from app.main.core.config import Config
from datetime import date, datetime


def default_json(o):
    if isinstance(o, (date, datetime)):
        return o.isoformat()


class NotificationPublisher:

    def __init__(self, host: str, port: int, db: int):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def publish(self, channel: str, type: str, data: dict):
        try:
            self.redis.publish(channel, json.dumps({'channel': channel, 'type': type, 'data': data}, default=default_json))
        except Exception as e:
            print(str(e))


notificationPublisher = NotificationPublisher(host=Config.REDIS_HOST if Config.IS_DEV else Config.REDIS_HOST_PROD, port=Config.REDIS_PORT, db=Config.REDIS_DB)
