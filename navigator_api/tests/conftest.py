import pytest

from navigator_api import model
from navigator_api.app import create_app
from navigator_api.tests import factories


@pytest.fixture()
def workflow():
    return factories.WorklowFactory()

@pytest.fixture(autouse=True, scope="session")
def setup():
    app = create_app('navigator_api.config.Testing')
    with app.app_context():
        model.db.create_all()
        yield
        model.db.drop_all()