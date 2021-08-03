from flask import Blueprint
from navigator_frontend.app import sio


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    sio.emit('navigate', {'fileurl': '/'})
    return 'Index'


@main_blueprint.route('/profile')
def profile():
    sio.emit('navigate', {'fileurl': 'profile'})
    return 'Profile'
