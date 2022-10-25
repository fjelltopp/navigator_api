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
        self.email_namespece = None
        self.require_auth = ResourceProtector()

    def init_app(self, app):
        self.issuer_url = app.config['AUTH0_DOMAIN']
        self.audience = app.config['AUTH0_AUDIENCE']
        self.email_namespece = app.config['AUTH0_EMAIL_NAMESPACE']

        validator = Auth0JWTBearerTokenValidator(
            self.issuer_url,
            self.audience
        )
        self.require_auth.register_token_validator(validator)

    def extract_email_from_token(self, token):
        return token[self.email_namespece]


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
