from flask import Flask
from flask_login import LoginManager

login = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    login.init_app(app)

    from navigator_api.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from navigator_api.main import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
