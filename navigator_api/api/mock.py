import logging
import time
from random import randint
from flask import Blueprint, jsonify
from flask_login import login_required
from webargs import fields
from webargs.flaskparser import use_args
from lorem import get_sentence

blueprint = Blueprint('mock', __name__)

# This is a mock API which when navigator_ui swiches to main.py should be removed
# remember to delete unused dependencies from Pipfile

@blueprint.route('/dataset/<dataset_id>/state', methods=['GET'])
@login_required
def dataset_state_get(dataset_id):
    possible_milestones = ['Shiny90', 'Naomi', 'Data Prep']
    possible_tasks = [
        "Generate input data",
        "Go to Spectrum/AIM. Row 34",
        "Download data templates from ADR",
        "Populate Shiny90 survey template",
        "Populate Shiny90 HIV testing template?",
        "Populate the Population template",
        "Populate ANC survey template",
        "Populate ART template",
        "Populate Naomi survey template",
        "Populate geo template",
        "Create user account",
    ]
    task_number = randint(2, 85)
    task_name = possible_tasks[
        randint(0, len(possible_tasks) - 1)
    ]
    list_items = ('').join([
        f'<li>{get_sentence(count=(1, 3))}</li>'
        for x in range(randint(1, 7))
    ])
    html = ''.join([
        f'<h3>{task_name}</h3>',
        f'<p>{get_sentence(count=(1, 3))}</p>',
        f'<ol>{list_items}</ol>'
    ])
    actionable_links = [
        {
            'label': possible_tasks[
                randint(0, len(possible_tasks) - 1)
            ],
            'link': 'http://example.com'
        }
        for x in range(randint(0, 3))
    ]
    return jsonify(
        {
            'task_number': task_number,
            'milestone': possible_milestones[randint(0, len(possible_milestones) - 1)],
            'display_html': html,
            'actionable_links': actionable_links,
            'skippable': bool(randint(0, 1)),
            'percentage': 5 if task_number < 5 else task_number,
            'grey': randint(0, 5),
            'last_updated': int(time.time())
        }
    )


@blueprint.route('/dataset/<dataset_id>/state', methods=['POST'])
@login_required
@use_args(
    {
        'action': fields.Str(required=True),
        'last_updated': fields.Int(required=True)
    }
)
def dataset_state_update(post_body, dataset_id):
    logging.info(post_body)
    assert post_body['action'] in ['next_step', 'skip_step']
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
