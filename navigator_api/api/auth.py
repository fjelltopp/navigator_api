import flask

from flask import Blueprint, request, jsonify, session
from flask_login import login_user, UserMixin, logout_user

from navigator_api.app import login
import navigator_api.clients.ckan_client as ckan_client

auth_blueprint = Blueprint('auth', __name__)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


@login.user_loader
def load_user(user_id):
    if 'ckan_user' in session:
        if session['ckan_user']['id'] == user_id:
            return User(id=user_id)
    return None


@auth_blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    remember = bool(request.json.get('remember', False))

    ckan_user = ckan_client.authenticate_user(password, username)
    if not ckan_user.get('email'):
        flask.abort(401, 'Bad credentials')
    else:
        user = User(id=ckan_user['id'])
        session['ckan_user'] = ckan_user
        login_user(user, remember=remember)
    return jsonify({"message": "Login successful"})


@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    logout_user()
    if 'ckan_user' in session:
        session.pop('ckan_user')
    return jsonify({"message": "Logout successful"})
