import logging
import json
from urllib.request import urlopen

from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.jose import JsonWebKey
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator

logger = logging.getLogger(__name__)


class Auth0Service:
    """Creates a decorator to auth protect resources with JWT OAuth2 token validation"""

    def __init__(self):
        self.issuer_url = None
        self.audience = None
        self.require_auth = ResourceProtector()

    def init_app(self, app):
        validator = Auth0JWTBearerTokenValidator(
            app.config['AUTH0_DOMAIN'],
            app.config['AUTH0_AUDIENCE']
        )
        self.require_auth.register_token_validator(validator)

class Auth0JWTBearerTokenValidator(JWTBearerTokenValidator):
    """Auth0 Validator to be used in Auth0Service"""
    def __init__(self, domain, audience):
        issuer = f"https://{domain}/"
        jsonurl = urlopen(f"{issuer}.well-known/jwks.json")
        public_key = JsonWebKey.import_key_set(
            json.loads(jsonurl.read())
        )
        super(Auth0JWTBearerTokenValidator, self).__init__(
            public_key
        )
        self.claims_options = {
            "exp": {"essential": True},
            "aud": {"essential": True, "value": audience},
            "iss": {"essential": True, "value": issuer},
        }


auth0_service = Auth0Service()
