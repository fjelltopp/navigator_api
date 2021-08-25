import logging
import redis
import os
from multiprocessing import Process

import functools

log = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME", "navigator_frontend")
redis_conn = redis.Redis(host=REDIS_URL, port=REDIS_PORT, charset="utf-8", decode_responses=True)


def subscribe(func):
    @functools.wraps(func)
    def handler():
        pubsub = redis_conn.pubsub()
        log.debug(f"Subscribing to pubsub {func.__name__}")
        pubsub.subscribe(func.__name__)
        for message in pubsub.listen():
            func(message['data'])

    Process(target=handler).start()
    return func


def response(event_queue):
    pubsub = redis_conn.pubsub()
    pubsub.subscribe(event_queue)
    print(f"Subscribed for response to: {event_queue}")
    for message in pubsub.listen():
        if message['data'] == 1:
            continue
        print(f"Received message {message}")
        if message['data']:
            yield 'data: %s\n\n' % message['data']
            pubsub.unsubscribe()
        else:
            yield 'data: no data\n\n'


def publish(event_type, event):
    redis_conn.publish(event_type, event)
