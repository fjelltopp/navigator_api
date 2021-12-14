from api.workflow.milestone import milestone_bp
from api.workflow.routes import workflow_bp
from api.workflow.task import task_bp

workflow_bp.register_blueprint(task_bp)
workflow_bp.register_blueprint(milestone_bp)
