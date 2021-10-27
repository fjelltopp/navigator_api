import logging
import time
from flask import Blueprint, jsonify, session
from flask_login import login_required
from webargs import fields
from webargs.flaskparser import use_args

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


@main_blueprint.route('/dataset_state', methods=['POST'])
@login_required
@use_args(
    {
        'dataset_id': fields.Int(required=True),
        'action': fields.Str(required=True),
        'last_updated': fields.Int(required=True)
    }
)
def dataset_state_update(post_body):
    logging.info(post_body)
    return jsonify({'success': True})
    # dataset_state = db.get_dataset_state(post_body['dataset_id'])
    # if dataset_state['last_updated'] != post_body['last_updated']:
    #     return jsonify({
    #         'message': 'Another user has already updated this dataset'
    #     }), 500
    # if post_body['action'] == 'next_step':
    #     db.dataset_next_step(post_body['dataset_id'])
    # elif post_body['action'] == 'skip_step':
    #     db.dataset_skip_step(post_body['dataset_id'])
    # else:
    #     return jsonify({'message': 'Invalid Action'}), 500
