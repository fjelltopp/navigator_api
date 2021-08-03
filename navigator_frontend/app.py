from flask import Flask
from flask_socketio import SocketIO

sio = SocketIO()


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
