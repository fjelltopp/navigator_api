import pytest

from navigator_api.tests import factories


@pytest.fixture()
def workflow():
    return factories.WorklowFactory()