import flask
import os

from flask import Blueprint, request, jsonify
import ckanapi
from flask_login import login_user, UserMixin, logout_user

from .app import login

auth_blueprint = Blueprint('auth', __name__)
CKAN_URL = os.getenv("CKAN_URL", "http://adr.local")
ckan = ckanapi.RemoteCKAN(CKAN_URL)


class User(UserMixin):
    def __init__(self, id, ckan_api_key):
        self.id = id
        self.ckan_api_key = ckan_api_key

    def get_id(self):
        #TODO: This should be refactored to not store the
        #ckan api in the session token. Consider storing
        #service level (sysadmin) access ckan api in navigator
        return f"{self.id}::{self.ckan_api_key}"


@login.user_loader
def load_user(_id):
    user_id, apikey = _id.split("::")
    return User(id=user_id, ckan_api_key=apikey)


@auth_blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    remember = bool(request.json.get('remember', False))

    ckan_user = ckan.action.user_login(id=username, password=password)
    if not ckan_user.get('email'):
        flask.abort(401, 'Bad credentials')
    else:
        user = User(id=ckan_user['id'], ckan_api_key=ckan_user['apikey'])
        login_user(user, remember=remember)
    return jsonify({"message": "Login successful"})


@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})
