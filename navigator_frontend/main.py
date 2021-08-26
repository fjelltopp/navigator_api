from flask import Blueprint, jsonify
from flask_login import login_required

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/')
def index():
    return 'Index'


@main_blueprint.route('/profile')
@login_required
def profile():
    return 'Profile'


@main_blueprint.route('/user_details')
@login_required
def user_details():
    return jsonify(
        {
            "firstName": "Manoj",
            "lastName": "Nathwani"
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
