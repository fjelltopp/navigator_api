import os

from flask import Flask
from flask_login import LoginManager
from flask_session import Session
from flask_cors import CORS

login = LoginManager()


def create_app(config_object=None):
    app = Flask(__name__)
    CORS(app)

    if not config_object:
        config_object = os.getenv('CONFIG_OBJECT', 'navigator_api.config.Config')
    app.config.from_object(config_object)
    app.url_map.strict_slashes = False

    login.init_app(app)
    Session(app)

    from navigator_api.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from navigator_api.main import main_blueprint
    app.register_blueprint(main_blueprint)

    from navigator_api.mock import blueprint as mock_blueprint
    app.register_blueprint(mock_blueprint)

    return app
