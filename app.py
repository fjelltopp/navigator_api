import os

import sentry_sdk
from flask import Flask
from flask_session import Session
from flask_cors import CORS
import json_logging
from sentry_sdk.integrations.flask import FlaskIntegration

from model import db, migrate
from api.auth import login_manager


def create_app(config_object=None):
    app = Flask(__name__)
    if not config_object:
        config_object = os.getenv('CONFIG_OBJECT', 'config.Config')
    app.config.from_object(config_object)
    app.url_map.strict_slashes = False

    if app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            environment=os.getenv("ENV_TYPE"),
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )

    CORS(app)
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    Session(app)
    if app.config['JSON_LOGGING']:
        json_logging.init_flask(enable_json=True)
        json_logging.init_request_instrument(app)

    from api.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from api.main import main_blueprint
    app.register_blueprint(main_blueprint)

    return app


app = create_app()
