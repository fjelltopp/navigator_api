from flask import Blueprint

from . import pubsub

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    pubsub.publish('navigate', "{'fileurl': '/'}")
    return 'Index'


@main_blueprint.route('/profile')
def profile():
    pubsub.publish('navigate', "{'fileurl': 'profile'}")
    return 'Profile'
