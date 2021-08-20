import os

import redis
from flask import Flask
from flask_socketio import SocketIO

sio = SocketIO()
REDIS_URL = os.getenv("REDIS_URL", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_QUEUE_NAME = os.getenv("REDIS_QUEUE_NAME", "navigator_frontend")
redis_conn = redis.Redis(host=REDIS_URL, port=REDIS_PORT, db=4, charset="utf-8", decode_responses=True)


@sio.on('app_created')
def created(data):
    print(f"app_created with {data}")


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    sio.init_app(app, message_queue='redis://redis:6379/4', async_mode='gevent_uwsgi')

    from navigator_frontend.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from navigator_frontend.main import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
