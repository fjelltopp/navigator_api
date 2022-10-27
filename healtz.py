import requests
from flask import Blueprint, current_app
from healthcheck import HealthCheck

import model

healthz_bp = Blueprint('healtz', __name__)


def db_available():
    try:
        model.db.session.execute("SELECT 1")
    except Exception as e:
        return False, str(e)
    return True, "db ok"


def engine_available():
    try:
        r = requests.get(current_app.config['ENGINE_URL'], timeout=2)
        if r.status_code != 200:
            return False, f"Engine returned http code {r.status_code}"
    except Exception as e:
        return False, str(e)
    return True, "engine ok"


def adr_available():
    try:
        r = requests.get(current_app.config['CKAN_URL'], timeout=2)
        if r.status_code != 200:
            return False, f"ADR returned http code {r.status_code}"
    except Exception as e:
        return False, str(e)
    return True, "adr ok"


health = HealthCheck()
health.add_check(db_available)
health.add_check(engine_available)
health.add_check(adr_available)


@healthz_bp.route('/healthz', methods=['GET'])
def healthz():
    return health.run()
