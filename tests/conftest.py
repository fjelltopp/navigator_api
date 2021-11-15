import uuid

import pytest

import model
from api.auth import User
from app import create_app
from tests import factories


@pytest.fixture()
def workflow():
    return factories.WorklowFactory()


@pytest.fixture()
def user():
    return User(id=str(uuid.uuid4()))


@pytest.fixture(scope="session")
def test_app():
    return create_app('config.Testing')


@pytest.fixture(scope="session")
def test_client(test_app):
    with test_app.test_client() as client:
        yield client


@pytest.fixture(autouse=True, scope="session")
def setup(test_app):
    with test_app.app_context():
        model.db.create_all()
        yield
        model.db.drop_all()
