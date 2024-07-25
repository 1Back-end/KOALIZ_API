import json
import time

import redis

from app.main.core.config import Config
from app.main.events.consumers.notification import NotificationConsume
from app.main.events.topics.consume_topics import ConsumeTopics

db = redis.Redis(
    host=Config.SUBSCRIBER_REDIS_HOST,
    port=Config.SUBSCRIBER_REDIS_PORT,
    decode_responses=True
)

consumer = db.pubsub()


def process_messages():
    consumer.subscribe(Config.SUBSCRIBER_REDIS_CHANNEL)
    for message in consumer.listen():
        print(message)
        if message.get('type') == 'message':
            data = json.loads(message.get('data'))
            message_type = data.get('type')
            data = data.get('data')
            if message_type == ConsumeTopics.EVENT_NEW_NOTIFICATION.value:
                return NotificationConsume.consume_general(data)

            print(f"messages ---> {message_type} -- {data}")
        time.sleep(0.5)
