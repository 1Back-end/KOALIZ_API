import json
import time

import redis

from app.main.core.config import Config

db = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True
)

def publish_messages(message_type: str, data: dict):
    message = json.dumps({"type": message_type, "data": data})
    db.publish(Config.REDIS_DB, message)
    print(message)
    time.sleep(1)