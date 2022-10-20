import uuid
from unittest.mock import patch

import pytest
import api.routes
import api.auth0_integration
import model
from api.auth import User
from app import create_app
from tests import factories


@pytest.fixture()
def workflow():
    return factories.WorklowFactory.create()


@pytest.fixture()
def user():
    return User(id=str(uuid.uuid4()))


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
def auth0_authorized():
    with patch('api.auth0_integration.ResourceProtector.acquire_token'):
        yield

