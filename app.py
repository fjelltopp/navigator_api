import os

import sentry_sdk
from flask import Flask, request
from flask_cors import CORS
import json_logging
from sentry_sdk.integrations.flask import FlaskIntegration
from flask_babel import Babel

import logic
from model import db, migrate
from api.auth import auth0_service


def create_app(config_object=None):
    app = Flask(__name__)
    if not config_object:
        config_object = os.getenv('CONFIG_OBJECT', 'config.Config')
    app.config.from_object(config_object)
    app.url_map.strict_slashes = False

    if app.config.get("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            environment=app.config["ENV_TYPE"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0
        )

    babel = Babel(app)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    auth0_service.init_app(app)
    if app.config['JSON_LOGGING']:
        json_logging.init_flask(enable_json=True)
        json_logging.init_request_instrument(app)

    from api import api_bp
    app.register_blueprint(api_bp)

    from healtz import healthz_bp
    app.register_blueprint(healthz_bp)

    @app.before_request
    def request_clear_cache():
        with logic.lock:
            logic.cache.clear()

    @babel.localeselector
    def get_locale():
        if request:
            return request.accept_languages.best_match(app.config['LANGUAGES'])
        else:
            return app.config['DEFAULT_LANGUAGE']

    return app


app = create_app()
