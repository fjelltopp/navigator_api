import os

from flask import Flask
from flask_session import Session
from flask_cors import CORS
import json_logging

from model import db, migrate
from api.auth import login_manager


def create_app(config_object=None):
    app = Flask(__name__)
    CORS(app)

    if not config_object:
        config_object = os.getenv('CONFIG_OBJECT', 'config.Config')
    app.config.from_object(config_object)
    app.url_map.strict_slashes = False

    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)
    json_logging.init_flask(enable_json=app.config['JSON_LOGGING'])
    json_logging.init_request_instrument(app)

    from api.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from api.main import main_blueprint
    app.register_blueprint(main_blueprint)

    return app


app = create_app()
