from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def get_workflow(dataset_id, user_id):
    return Workflow.query.filter_by(dataset_id=dataset_id, user_id=user_id).first()


def get_workflows(user_id):
    return Workflow.query.filter_by(user_id=user_id).all()


class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    decision_engine_id = db.Column(db.String, nullable=False)
    dataset_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    _skipped_tasks = db.Column(db.String, default='')

    @property
    def skipped_tasks(self):
        if len(self._skipped_tasks) == 0:
            return []
        return [x for x in self._skipped_tasks.split(';')]

    @skipped_tasks.setter
    def skipped_tasks(self, tasks_list):
        self._skipped_tasks = ';'.join(tasks_list)
