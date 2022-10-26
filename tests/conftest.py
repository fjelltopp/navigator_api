from unittest.mock import patch

import pytest
import model
from app import create_app
from helpers import ckan_client_test_double
from tests import factories


@pytest.fixture()
def workflow():
    return factories.WorklowFactory.create()


@pytest.fixture(scope="session")
def test_app():
    return create_app('config.Testing')


@pytest.fixture
def test_client(test_app):
    with test_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def setup(test_app):
    with test_app.app_context():
        model.db.create_all()
        yield
        model.db.session.close_all()
        model.db.drop_all()


@pytest.fixture
def auth0_authorized(test_app):
    current_token_mock = {
        test_app.config['AUTH0_EMAIL_NAMESPACE']: ckan_client_test_double.valid_user_email
    }
    with patch('api.auth.ResourceProtector.acquire_token'):
        with patch('api.auth.current_token', new=current_token_mock):
            yield
