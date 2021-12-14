from flask import Blueprint, jsonify
from flask_login import login_required

milestone_bp = Blueprint('milestone', __name__,)


@milestone_bp.route('/workflows/<dataset_id>/milestones/<milestone_id>', methods=['GET'])
@login_required
def workflow_milestone_details(dataset_id, milestone_id):
    return jsonify({
        "id": "EST-MIL-01-10-M",
        "progress": 20,
        "tasks": [
            {
                "completed": True,
                "id": "EST-OVV-01-10-A",
                "manual": True,
                "milestoneID": "EST-MIL-01-10-M",
                "reached": True,
                "skipped": False,
                "title": "Welcome to the UNAIDS HIV Estimates Navigator"
            },
            {
                "completed": False,
                "id": "EST-OVV-01-11-A",
                "manual": True,
                "milestoneID": "EST-MIL-01-10-M",
                "reached": True,
                "skipped": False,
                "title": "Navigator tutorial: Skipping tasks"
            }
        ],
        "title": "Navigator Tutorial"
    })
