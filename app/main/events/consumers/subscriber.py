import json
import time

import redis

from app.main.core.config import Config
from app.main.events.consumers.notification import NotificationConsume

db = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True
)

consumer = db.pubsub()


def process_messages():
    consumer.subscribe(Config.REDIS_DB)
    for message in consumer.listen():
        print(message)
        if message.get('type') == 'message':
            data = json.loads(message.get('data'))
            message_type = data.get('type')
            data = data.get('data')
            return NotificationConsume.consume_general(data)

            print(f"messages ---> {message_type} -- {data}")
        time.sleep(0.5)
