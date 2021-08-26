from flask import Blueprint


main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return 'Index'

@main_blueprint.route('/profile')
def profile():
    return 'Profile'
