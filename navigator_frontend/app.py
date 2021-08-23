from flask import Flask
from . pubsub import subscribe


@subscribe
def app_created(data):
    print(f"app_created with {data}")


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    from navigator_frontend.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from navigator_frontend.main import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
