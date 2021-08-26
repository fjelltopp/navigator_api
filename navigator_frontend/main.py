from flask import Blueprint
from flask_login import login_required

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return 'Index'

@main_blueprint.route('/profile')
@login_required
def profile():
    return 'Profile'
