from flask import Blueprint, jsonify, session
from flask_login import login_required

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return 'Index'


@main_blueprint.route('/profile')
@login_required
def profile():
    return 'Profile'


@main_blueprint.route('/user')
@login_required
def user_details():
    user_details = session['ckan_user']
    return jsonify(
        {
            "fullname": user_details["fullname"],
            "email": user_details["email"],
        }
    )


@main_blueprint.route('/datasets')
@login_required
def datasets():
    return jsonify(
        {
            "datasets": [
                {
                    "id": "1",
                    "name": "Uganda Inputs UNAIDS Estimates 2021"
                },
                {
                    "id": "2",
                    "name": "Malawi Inputs UNAIDS Estimates 2021"
                },
                {
                    "id": "3",
                    "name": "Antarctica Inputs UNAIDS Estimates 2021"
                }
            ]
        }
    )