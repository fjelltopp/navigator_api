from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    decision_engine_id = db.Column(db.String, nullable=False)
    dataset_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, nullable=False)
    _skipped_tasks = db.Column(db.String, default='')

    @property
    def skipped_tasks(self):
        return [x for x in self._skipped_tasks.split(';')]

    @skipped_tasks.setter
    def skipped_tasks(self, tasks_list):
        self._skipped_tasks = ';'.join(tasks_list)


