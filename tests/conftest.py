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


@pytest.fixture(autouse=True, scope="session")
def setup():
    app = create_app('config.Testing')
    with app.app_context():
        model.db.create_all()
        yield
        model.db.drop_all()
