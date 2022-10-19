import logging

from flask import Blueprint, url_for
from flask.sessions import SecureCookieSessionInterface
from flask_login import UserMixin

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


class User(UserMixin):
    def __init__(self, id):
        self.id = id


class SkipForInternalSessionInterface(SecureCookieSessionInterface):
    """Prevent creating session for internal requests."""

    def open_session(self, app, _request):
        if _request.path == url_for('healtz.healthz'):
            return None
        return super(SkipForInternalSessionInterface, self).open_session(app, _request)

