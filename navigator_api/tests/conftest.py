import uuid

import pytest

from navigator_api import model
from navigator_api.api.auth import User
from navigator_api.app import create_app
from navigator_api.tests import factories


@pytest.fixture()
def workflow():
    return factories.WorklowFactory()


@pytest.fixture()
def user():
    return User(id=str(uuid.uuid4()))


@pytest.fixture(autouse=True, scope="session")
def setup():
    app = create_app('navigator_api.config.Testing')
    with app.app_context():
        model.db.create_all()
        yield
        model.db.drop_all()
