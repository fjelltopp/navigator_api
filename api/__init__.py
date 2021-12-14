from api.workflow import workflow_bp
from api.routes import api_bp

api_bp.register_blueprint(workflow_bp)
