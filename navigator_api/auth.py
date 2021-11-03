import flask
import os

from flask import Blueprint, request, jsonify, session
import ckanapi
from flask_login import login_user, UserMixin, logout_user

from .app import login

auth_blueprint = Blueprint('auth', __name__)
CKAN_URL = os.getenv("CKAN_URL", "http://adr.local")
ckan = ckanapi.RemoteCKAN(CKAN_URL)


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

    ckan_user = ckan.action.user_login(id=username, password=password)
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
